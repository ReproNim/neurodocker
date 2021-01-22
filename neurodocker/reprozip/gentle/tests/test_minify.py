from pathlib import Path
from unittest.mock import patch

import pytest

from neurodocker.reprozip.gentle.trace import trace_and_prune

reprozip = pytest.importorskip("reprozip", reason="reprozip not found")
docker = pytest.importorskip("docker", reason="docker-py not found")


def test_trace_and_prune():
    client = docker.from_env()
    container = client.containers.run(
        "python:3.8-slim", detach=True, tty=True, security_opt=["seccomp:unconfined"]
    )

    commands = ["python --version", "python -c print()"]

    try:
        # Respond yes to delete things.
        with patch("builtins.input", return_value="y"):
            trace_and_prune(container.name, commands, "/usr/local")

        for cmd in commands:
            ret, result = container.exec_run(cmd)
            result = result.decode()
            if ret:
                assert (
                    False
                ), "unexpected non-zero return code when running '{}'".format(cmd)

        # This should fail.
        ret, result = container.exec_run("pip --help")
        if not ret:
            assert False, "unexpected zero return code when running '{}'".format(cmd)

    finally:
        container.stop()
        container.remove()


def test_trace_and_prune_with_mounted_volume(tmp_path: Path):
    client = docker.from_env()

    # Create a file in a mounted directory.
    (tmp_path / "foobar.txt").write_text("Foobar")

    container = client.containers.run(
        "python:3.8-slim",
        detach=True,
        tty=True,
        security_opt=["seccomp:unconfined"],
        volumes={str(tmp_path): {"bind": "/work", "mode": "rw"}},
    )

    commands = ["python --version", "python -c print()"]

    try:
        # Respond yes to delete things.
        with patch("builtins.input", return_value="y"):
            with pytest.raises(ValueError):
                trace_and_prune(container, commands, ["/usr/local", "/work"])

        # This should work.
        with patch("builtins.input", return_value="y"):
            trace_and_prune(container, commands, ["/usr/local"])
    finally:
        container.stop()
        container.remove()
