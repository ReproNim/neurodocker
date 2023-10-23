from pathlib import Path

import pytest
from click.testing import CliRunner

from neurodocker.cli.cli import generate, genfromjson
from neurodocker.reproenv.state import _TemplateRegistry
from neurodocker.reproenv.tests.utils import (
    get_build_and_run_fns,
    skip_if_no_docker,
    skip_if_no_singularity,
)

# Test that a template can be rendered
# We need to use `reproenv generate` as the entrypoint here because the generate command
# is what registers the templates. Using the `docker` function
# (`reproenv generate docker`) directly does not fire `generate`.


@pytest.mark.long
@pytest.mark.parametrize(
    "cmd",
    [
        pytest.param("docker", marks=skip_if_no_docker),
        pytest.param("singularity", marks=skip_if_no_singularity),
    ],
)
@pytest.mark.parametrize(
    ["pkg_manager", "base_image"], [("apt", "debian:buster-slim"), ("yum", "centos:7")]
)
def test_build_image_from_registered(
    tmp_path: Path, cmd: str, pkg_manager: str, base_image: str
):
    # Templates are in this directory.
    template_path = Path(__file__).parent
    runner = CliRunner(env={"REPROENV_TEMPLATE_PATH": str(template_path)})
    _TemplateRegistry._reset()
    result = runner.invoke(
        generate,
        [
            "--template-path",
            str(template_path),
            cmd,
            "--base-image",
            base_image,
            "--pkg-manager",
            pkg_manager,
            "--jq",
            "version=1.5",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "jq-1.5/jq-linux64" in result.output

    spec = "Dockerfile" if cmd == "docker" else "Singularity"
    (tmp_path / spec).write_text(result.output)

    build_fn, run_fn = get_build_and_run_fns(cmd)
    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img, args=["jq", "--help"])
        assert "jq is a tool for processing JSON" in stdout


@pytest.mark.long
@pytest.mark.parametrize(
    "cmd",
    [
        pytest.param("docker", marks=skip_if_no_docker),
        pytest.param("singularity", marks=skip_if_no_singularity),
    ],
)
@pytest.mark.parametrize("inputs", ["file", "stdin"])
def test_json_roundtrip(cmd: str, inputs: str, tmp_path: Path):
    """Test that we can generate a JSON representation of a container and build an
    identical container with it.
    """
    _TemplateRegistry._reset()
    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            cmd,
            "--json",
            "--base-image",
            "debian:buster-slim",
            "--pkg-manager",
            "apt",
            "--install",
            "git",
            "--env",
            "CAT=FOO",
            "DOG=BAR",
        ],
    )
    assert result.exit_code == 0, result.output
    (tmp_path / "specs.json").write_text(result.output)

    if inputs == "file":
        result = runner.invoke(genfromjson, [cmd, str(tmp_path / "specs.json")])
    elif inputs == "stdin":
        json_input = (tmp_path / "specs.json").read_text()
        result = runner.invoke(genfromjson, [cmd, "-"], input=json_input)
    else:
        raise ValueError(f"unknown inputs: {inputs}")

    spec = "Dockerfile" if cmd == "docker" else "Singularity"
    (tmp_path / spec).write_text(result.output)

    build_fn, run_fn = get_build_and_run_fns(cmd)
    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img, args=["git", "--help"])
        assert "commit" in stdout
        stdout, _ = run_fn(img, args=["env"])
        assert "CAT=FOO" in stdout
        assert "DOG=BAR" in stdout
