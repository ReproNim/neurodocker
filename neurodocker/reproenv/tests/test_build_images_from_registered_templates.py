# TODO: add more tests for `from_dict` method.

from pathlib import Path
import subprocess
import typing as ty

import pytest

from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.renderers import SingularityRenderer
from neurodocker.reproenv.state import _TemplateRegistry
from neurodocker.reproenv.tests.utils import singularity_build
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

    if cmd == "docker":
        import docker

        client = docker.from_env()
        r = DockerRenderer.from_dict(d)
        # Write Dockerfile.
        (tmp_path / "Dockerfile").write_text(str(r))
        image = client.images.build(path=str(tmp_path), tag="jq", rm=True)
        # This is a tuple...
        image = image[0]
        stdout = client.containers.run(image=image, command="jq --help")
        assert stdout.decode().strip().startswith("jq - commandline JSON processor")
        stdout = client.containers.run(image=image, command="jq --version")
        assert stdout.decode().strip() == jq_version_output
        # Test that deb was installed
        stdout = client.containers.run(image=image, command=f"{fd_exe} --version")
        assert stdout.decode().strip().startswith(fd_version_startswith)

    elif cmd == "singularity":
        # Create a Singularity recipe
        r = SingularityRenderer.from_dict(d)
        # Write Singularity recipe
        sing_path = tmp_path / "Singularity"
        sif_path = tmp_path / "jq-test.sif"
        sing_path.write_text(str(r))
        # Build
        _ = singularity_build(image_path=sif_path, build_spec=sing_path, cwd=tmp_path)
        # Test
        completed = subprocess.run(
            f"singularity run {sif_path} jq --help".split(),
            capture_output=True,
            check=True,
        )
        assert (
            completed.stdout.decode()
            .strip()
            .startswith("jq - commandline JSON processor")
        )
        completed = subprocess.run(
            f"singularity run {sif_path} jq --version".split(),
            capture_output=True,
            check=True,
        )
        assert completed.stdout.decode().strip() == jq_version_output
        # Test that deb was installed
        completed = subprocess.run(
            f"singularity run {sif_path} {fd_exe} --version".split(),
            capture_output=True,
            check=True,
        )
        assert completed.stdout.decode().strip().startswith(fd_version_startswith)

    else:
        raise ValueError("unknown container type")


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

    if cmd == "docker":
        import docker

        client = docker.from_env()

        r = DockerRenderer(pkg_manager=pkg_manager)
        r.from_(base_image)
        r.add_registered_template("jq", method=method, version=jq_version)

        # Write Dockerfile.
        (tmp_path / "Dockerfile").write_text(str(r))
        image = client.images.build(path=str(tmp_path), tag="jq", rm=True)
        # This is a tuple...
        image = image[0]
        stdout = client.containers.run(image=image, command="jq --help")
        assert stdout.decode().strip().startswith("jq - commandline JSON processor")
        stdout = client.containers.run(image=image, command="jq --version")
        if method == "source" and jq_version == "1.5":
            assert stdout.decode().strip() == "jq-"
        else:
            assert stdout.decode().strip() == jq_version_output
        # Test that deb was installed
        if method == "binaries":
            stdout = client.containers.run(image=image, command=f"{fd_exe} --version")
            assert stdout.decode().strip().startswith(fd_version_startswith)

    elif cmd == "singularity":
        # Create a Singularity recipe.
        sr = SingularityRenderer(pkg_manager=pkg_manager)
        sr.from_(base_image)
        sr.add_registered_template("jq", method=method, version=jq_version)

        # Write Singularity recipe.
        sing_path = tmp_path / "Singularity"
        sif_path = tmp_path / "jq-test.sif"
        sing_path.write_text(str(sr))
        _ = singularity_build(image_path=sif_path, build_spec=sing_path, cwd=tmp_path)
        completed = subprocess.run(
            f"singularity run {sif_path} jq --help".split(),
            capture_output=True,
            check=True,
        )
        assert (
            completed.stdout.decode()
            .strip()
            .startswith("jq - commandline JSON processor")
        )
        completed = subprocess.run(
            f"singularity run {sif_path} jq --version".split(),
            capture_output=True,
            check=True,
        )
        if method == "source" and jq_version == "1.5":
            assert completed.stdout.decode().strip() == "jq-"
        else:
            assert completed.stdout.decode().strip() == jq_version_output

        # Test that deb was installed
        if pkg_manager == "apt" and method == "binaries":
            completed = subprocess.run(
                f"singularity run {sif_path} {fd_exe} --version".split(),
                capture_output=True,
                check=True,
            )
            assert completed.stdout.decode().strip().startswith(fd_version_startswith)

    else:
        raise ValueError("unknown container type")
