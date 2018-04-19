"""Tests for trace.py."""

from __future__ import absolute_import, division, print_function

import os
import tempfile

import pytest

from neurodocker.reprozip.trace import ReproZipMinimizer
from neurodocker.utils import get_docker_client


def test_ReproZipMinimizer_no_ptrace():
    client = get_docker_client()
    container = client.containers.run('debian:stretch', detach=True, tty=True)

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(container.id, commands,
                                      packfile_save_dir=tmpdir)
        with pytest.raises(RuntimeError):  # ptrace should fail
            minimizer.run()
    except Exception:
        raise
    finally:
        container.stop()
        container.remove()


def test_ReproZipMinimizer():
    client = get_docker_client()
    container = client.containers.run(
        'debian:stretch', detach=True, tty=True,
        security_opt=['seccomp:unconfined'])

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(
            container.id, commands, packfile_save_dir=tmpdir)
        packfile_path = minimizer.run()
    except Exception:
        raise
    finally:
        container.stop()
        container.remove()

    assert os.path.isfile(packfile_path), "Pack file not saved."
