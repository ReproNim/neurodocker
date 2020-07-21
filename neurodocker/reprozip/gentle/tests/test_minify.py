"""Tests for trace.py."""

import os
import unittest

import pytest

from neurodocker.utils import get_docker_client
from neurodocker.reprozip.gentle.trace import trace_and_prune

try:
    import reprozip

    have_reprozip = True
except ImportError:
    have_reprozip = False

needs_reprozip = unittest.skipUnless(have_reprozip, "These tests need reprozip")


@needs_reprozip
def test_trace_and_prune():
    client = get_docker_client()
    container = client.containers.run(
        "python:3.8-slim", detach=True, tty=True, security_opt=["seccomp:unconfined"]
    )

    commands = ["python --version", "python -c print()"]

    try:
        # Respond yes to delete things.
        with unittest.mock.patch("builtins.input", return_value="y"):
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


@needs_reprozip
def test_trace_and_prune_with_mounted_volume(tmpdir):
    client = get_docker_client()

    # Create a file in a mounted directory.
    with (tmpdir / "foobar.txt").open("w", encoding="utf-8") as f:
        f.write("Foobar")

    container = client.containers.run(
        "python:3.8-slim",
        detach=True,
        tty=True,
        security_opt=["seccomp:unconfined"],
        volumes={str(tmpdir): {"bind": "/work", "mode": "rw"}},
    )

    commands = ["python --version", "python -c print()"]

    try:
        # Respond yes to delete things.
        with unittest.mock.patch("builtins.input", return_value="y"):
            with pytest.raises(ValueError):
                trace_and_prune(container.name, commands, ["/usr/local", "/work"])

        # This should work.
        with unittest.mock.patch("builtins.input", return_value="y"):
            trace_and_prune(container.name, commands, ["/usr/local"])
    finally:
        container.stop()
        container.remove()
