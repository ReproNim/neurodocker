"""Tests for trace.py."""

from __future__ import absolute_import, division, print_function

import os
import tempfile

import pytest

from neurodocker.docker import client
from neurodocker.reprozip.trace import ReproZipMinimizer


@pytest.mark.skip(reason="seccomp not available in ubuntu trusty (travis)")
def test_ReproZipMinimizer_no_ptrace():
    container = client.containers.run('debian:stretch', detach=True, tty=True)

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(container.id, commands,
                                      packfile_save_dir=tmpdir)
        with pytest.raises(RuntimeError):  # ptrace should fail
            minimizer.run()
    except:
        raise
    finally:
        container.stop()
        container.remove()


def test_ReproZipMinimizer():
    container = client.containers.run('debian:stretch', detach=True, tty=True,
                                      security_opt=['seccomp:unconfined'])

    commands = ["du --help", "ls --help"]
    tmpdir = tempfile.mkdtemp()
    try:
        minimizer = ReproZipMinimizer(container.id, commands,
                                      packfile_save_dir=tmpdir)
        packfile_path = minimizer.run()
    except:
        raise
    finally:
        container.stop()
        container.remove()

    assert os.path.isfile(packfile_path), "Pack file not saved."
