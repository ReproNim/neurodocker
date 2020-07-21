"""Tests for trace.py."""

import os
import tempfile
import unittest

import pytest

from neurodocker.reprozip.trace import ReproZipMinimizer
from neurodocker.utils import get_docker_client

try:
    import reprozip

    have_reprozip = True
except ImportError:
    have_reprozip = False

needs_reprozip = unittest.skipUnless(have_reprozip, "These tests need reprozip")


@pytest.mark.skip(reason="seccomp not available in CI")
@needs_reprozip
def test_ReproZipMinimizer_no_ptrace():
    client = get_docker_client()
    container = client.containers.run("debian:stretch", detach=True, tty=True)

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(container.id, commands, packfile_save_dir=tmpdir)
        with pytest.raises(RuntimeError):  # ptrace should fail
            minimizer.run()
    except Exception:
        raise
    finally:
        container.stop()
        container.remove()


@needs_reprozip
def test_ReproZipMinimizer():
    client = get_docker_client()
    container = client.containers.run(
        "debian:stretch", detach=True, tty=True, security_opt=["seccomp:unconfined"]
    )

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(container.id, commands, packfile_save_dir=tmpdir)
        packfile_path = minimizer.run()
    except Exception:
        raise
    finally:
        container.stop()
        container.remove()

    assert os.path.isfile(packfile_path), "Pack file not saved."
