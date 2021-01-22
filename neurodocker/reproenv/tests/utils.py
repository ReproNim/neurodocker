import getpass
import os
from pathlib import Path
import subprocess
import typing as ty

import pytest

# TODO: do not use the docker-py package. It is better to be consistent and use
# subprocess for Docker and Singularity. In both cases, we are only
# TODO: only require docker-py for container minification, as it is more useful there
# to get logs as the container is building.
try:
    import docker
except ImportError:
    docker = None


def _docker_available():
    """Return `True` if docker-py is installed and docker engine is available."""
    if docker is None:
        return False
    client = docker.from_env()
    try:
        return client.ping()  # bool, unless engine is unresponsive (eg not installed)
    except docker.errors.APIError:
        return False


def _singularity_available():
    try:
        process = subprocess.run(["singularity", "help"])
        return process.returncode == 0
    except FileNotFoundError:
        return False


# See https://docs.pytest.org/en/stable/skipping.html#id1 for skipif.

skip_if_no_docker = pytest.mark.skipif(
    not _docker_available(), reason="docker not available"
)

skip_if_no_singularity = pytest.mark.skipif(
    not _singularity_available(), reason="singularity not available"
)


def singularity_build(
    image_path: ty.Union[os.PathLike, str],
    build_spec: ty.Union[os.PathLike, str],
    cwd: ty.Union[os.PathLike, str] = None,
) -> subprocess.CompletedProcess:
    """Wrapper for `singularity build`.

    If `sudo singularity` is not available, the full path to `singularity` can be set
    with the environment variable `REPROENV_SINGULARITY_PROGRAM`.
    """
    user = getpass.getuser()
    # Set singularity cache to /dev/shm
    cachedir = Path("/") / "dev" / "shm" / user / "singularity"
    singularity = os.environ.get("REPROENV_SINGULARITY_PROGRAM", "singularity")
    cmds = [
        "sudo",
        f"SINGULARITY_CACHEDIR={cachedir}",
        singularity,
        "build",
        str(image_path),
        str(build_spec),
    ]
    return subprocess.run(cmds, check=True, cwd=cwd)
