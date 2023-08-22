from __future__ import annotations

import contextlib
import getpass
import os
import subprocess
import uuid
from pathlib import Path
from typing import Generator

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
    """Return `True` if docker-py is installed or docker engine is available."""
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


@contextlib.contextmanager
def build_docker_image(context: Path, remove=False) -> Generator[str, None, None]:
    """Context manager that builds a Docker image and removes it on exit.

    The argument `remove` is `False` by default because we clean up all images at the
    end of each pytest session.

    Yields
    ------
    str
        Docker image tag.
    """
    df = context / "Dockerfile"
    if not df.exists():
        raise FileNotFoundError(f"Dockerfile not found: {df}")
    tag = "reproenv-pytest-" + uuid.uuid4().hex
    cmd: list[str] = ["docker", "build", "--tag", tag, str(context)]
    try:
        _ = subprocess.check_output(cmd, cwd=context)
        yield tag
    finally:
        # There is no container to remove. That should be done by the tests.
        # Containers made from this image _need_ to be removed for this image to be
        # removed.
        # Do not force image removal, because perhaps others depend on the image.
        # TODO: we do not make use of Docker's caching if we remove...
        if remove:
            subprocess.run(["docker", "image", "rm", tag])
            subprocess.run(["docker", "builder", "prune", "--force"])


@contextlib.contextmanager
def build_singularity_image(context: Path, remove=True) -> Generator[str, None, None]:
    """Context manager that builds a Apptainer image and removes it on exit.

    If `sudo singularity` is not available, the full path to `apptainer` can be set
    with the environment variable `REPROENV_APPTAINER_PROGRAM`.

    Yields
    ------
    Path
        Path to Singularity image.
    """
    recipe = context / "Singularity"
    if not recipe.exists():
        raise FileNotFoundError(f"Apptainer recipe not found: {recipe}")
    sif = context / f"reproenv-pytest-{uuid.uuid4().hex}.sif"
    # Set apptainer cache to /dev/shm
    user = getpass.getuser()
    cachedir = Path("/") / "dev" / "shm" / user / "apptainer"
    singularity = os.environ.get("REPROENV_APPTAINER_PROGRAM", "apptainer")
    cmd: list[str] = [
        "sudo",
        f"APPTAINER_CACHEDIR={cachedir}",
        singularity,
        "build",
        str(sif),
        str(recipe),
    ]
    try:
        _ = subprocess.check_output(cmd, cwd=context)
        yield str(sif)
    finally:
        if remove:
            try:
                sif.unlink()
            except FileNotFoundError:
                pass


def run_docker_image(img: str, args: list[str] = None, entrypoint: list[str] = None):
    """Wrapper for `docker run`.

    Returns
    -------
    str, str
        Stdout and stderr of the process.
    """
    cmd = ["docker", "run", "--rm", "-i"]
    if entrypoint is not None:
        cmd.extend(["--entrypoint", *entrypoint])
    cmd.append(img)
    if args is not None:
        cmd.extend(args)
    print(" ".join(cmd))
    process = subprocess.run(cmd, capture_output=True, check=True)
    stdout = process.stdout.decode().strip()
    stderr = process.stderr.decode().strip()
    return stdout, stderr


def run_singularity_image(
    img: str, args: list[str] = None, entrypoint: list[str] = None
):
    """Wrapper for `singularity run` or `singularity exec`.

    Returns
    -------
    str, str
        Stdout and stderr of the process.
    """
    scmd = "run" if entrypoint is None else "exec"
    # sudo not required
    cmd: list[str] = ["singularity", scmd, "--cleanenv", img]
    if entrypoint is not None:
        cmd.extend(entrypoint)
    if args is not None:
        cmd.extend(args)
    process = subprocess.run(cmd, capture_output=True, check=True)
    stdout = process.stdout.decode().strip()
    stderr = process.stderr.decode().strip()
    return stdout, stderr


def get_build_and_run_fns(cmd: str):
    cmd = cmd.lower()
    if cmd == "docker":
        return build_docker_image, run_docker_image
    elif cmd == "singularity":
        return build_singularity_image, run_singularity_image
    else:
        raise KeyError(f"unknown cmd: {cmd}")


def prune_rendered(r: str) -> str:
    # Remove portion that saves JSON to file.
    lines = r.splitlines()
    start_bad = lines.index("# Save specification to JSON.")
    end_bad = lines.index("# End saving to specification to JSON.")
    new_lines = lines[: start_bad - 1] + lines[end_bad + 1 :]
    r = "\n".join(new_lines)

    # Remove comments.
    # This part has to happen _after_ removing the JSON, because
    # JSON is removed based on a certain comment.
    r = "\n".join(line for line in r.splitlines() if not line.startswith("#"))

    # TODO: should we remove empty lines?

    return r
