# TODO: add more tests for `from_dict` method.

from pathlib import Path
import typing as ty

import pytest

from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.renderers import SingularityRenderer
from neurodocker.reproenv.state import _TemplateRegistry
from neurodocker.reproenv.tests.utils import get_build_and_run_fns
from neurodocker.reproenv.tests.utils import skip_if_no_docker
from neurodocker.reproenv.tests.utils import skip_if_no_singularity
from neurodocker.reproenv.types import installation_methods_type
from neurodocker.reproenv.types import pkg_managers_type

_template_filepath = Path(__file__).parent / "sample-template-jq.yaml"


@pytest.mark.verylong
@pytest.mark.parametrize(
    "cmd",
    [
        pytest.param("docker", marks=skip_if_no_docker),
        pytest.param("singularity", marks=skip_if_no_singularity),
    ],
)
@pytest.mark.parametrize(
    ["pkg_manager", "base_image"], [("apt", "debian:buster-slim"), ("yum", "fedora:33")]
)
@pytest.mark.parametrize(
    ["jq_version", "jq_version_output", "fd_version_startswith"],
    [("1.6", "jq-1.6", "fd")],
)
def test_build_using_renderer_from_dict(
    cmd: str,
    pkg_manager: str,
    base_image: str,
    jq_version: str,
    jq_version_output: str,
    fd_version_startswith: str,
    tmp_path: Path,
):

    _TemplateRegistry._reset()
    _TemplateRegistry.register(_template_filepath)

    d = {
        "pkg_manager": pkg_manager,
        "instructions": [
            {"name": "from_", "kwds": {"base_image": base_image}},
            {"name": "run", "kwds": {"command": "echo hello there"}},
            {"name": "jq", "kwds": {"version": jq_version, "method": "binaries"}},
        ],
    }

    fd_exe = "fdfind" if pkg_manager == "apt" else "fd"

    rcls = DockerRenderer if cmd == "docker" else SingularityRenderer
    specf = "Dockerfile" if cmd == "docker" else "Singularity"

    r = rcls.from_dict(d)
    (tmp_path / specf).write_text(str(r))

    build_fn, run_fn = get_build_and_run_fns(cmd)
    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img, args=["jq", "--help"])
        assert stdout.startswith("jq - commandline JSON processor")
        stdout, _ = run_fn(img, args=["jq", "--version"])
        assert stdout == jq_version_output
        # Test that deb was installed
        stdout, _ = run_fn(img, args=[fd_exe, "--version"])
        assert stdout.startswith(fd_version_startswith)


@pytest.mark.verylong
@pytest.mark.parametrize(
    "cmd",
    [
        pytest.param("docker", marks=skip_if_no_docker),
        pytest.param("singularity", marks=skip_if_no_singularity),
    ],
)
@pytest.mark.parametrize(
    ["pkg_manager", "base_image"], [("apt", "debian:buster-slim"), ("yum", "fedora:33")]
)
@pytest.mark.parametrize(["method"], [("binaries",), ("source",)])
@pytest.mark.parametrize(
    ["jq_version", "jq_version_output", "fd_version_startswith"],
    [("1.6", "jq-1.6", "fd"), ("1.5", "jq-1.5", "fd")],
)
def test_build_using_renderer_instance_methods(
    cmd: str,
    pkg_manager: str,
    base_image: str,
    method: str,
    jq_version: str,
    jq_version_output: str,
    fd_version_startswith: str,
    tmp_path: Path,
):
    _TemplateRegistry._reset()
    _TemplateRegistry.register(_template_filepath)

    pkg_manager = ty.cast(pkg_managers_type, pkg_manager)
    method = ty.cast(installation_methods_type, method)

    fd_exe = "fdfind" if pkg_manager == "apt" else "fd"

    rcls = DockerRenderer if cmd == "docker" else SingularityRenderer
    r = rcls(pkg_manager=pkg_manager)
    r.from_(base_image)
    r.add_registered_template("jq", method=method, version=jq_version)
    specf = "Dockerfile" if cmd == "docker" else "Singularity"
    (tmp_path / specf).write_text(str(r))

    build_fn, run_fn = get_build_and_run_fns(cmd)
    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img, args=["jq", "--help"])
        assert stdout.startswith("jq - commandline JSON processor")
        stdout, _ = run_fn(img, args=["jq", "--version"])
        if method == "source" and jq_version == "1.5":
            assert stdout == "jq-"
        else:
            assert stdout == jq_version_output
        # Test that deb was installed
        if method == "binaries":
            stdout, _ = run_fn(img, args=[fd_exe, "--version"])
            assert stdout.startswith(fd_version_startswith)
