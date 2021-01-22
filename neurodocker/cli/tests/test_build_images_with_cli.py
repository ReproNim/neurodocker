from pathlib import Path
import subprocess

from click.testing import CliRunner
import pytest

from neurodocker.cli.cli import generate
from neurodocker.reproenv.state import _TemplateRegistry
from neurodocker.reproenv.tests.utils import singularity_build
from neurodocker.reproenv.tests.utils import skip_if_no_docker
from neurodocker.reproenv.tests.utils import skip_if_no_singularity

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
    import docker

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

    if cmd == "docker":
        # build docker image
        (tmp_path / "Dockerfile").write_text(result.output)
        client = docker.from_env()
        image = client.images.build(path=str(tmp_path), tag="reproenvtest", rm=True)
        image = image[0]  # This is a tuple...
        stdout = client.containers.run(image=image, command="jq --help")
        assert "jq is a tool for processing JSON" in stdout.decode().strip()

    elif cmd == "singularity":
        # build singularity image
        sing_path = tmp_path / "Singularity"
        sif_path = tmp_path / "test.sif"
        sing_path.write_text(result.output)
        _ = singularity_build(image_path=sif_path, build_spec=sing_path, cwd=tmp_path)
        completed = subprocess.run(
            f"singularity run {sif_path} jq --help".split(),
            capture_output=True,
            check=True,
        )
        assert "jq is a tool for processing JSON" in completed.stdout.decode()

    else:
        raise ValueError(f"unknown command: {cmd}")
