"""Tests for merge.py."""

from __future__ import absolute_import, division, print_function

from glob import glob
import os
import tarfile
import tempfile

from neurodocker.reprozip.trace import ReproZipMinimizer
from neurodocker.utils import get_docker_client
from neurodocker.reprozip.merge import merge_pack_files


def _create_packfile(commands, dir):
    """Create packfile from list `commands` in debian:stretch container."""
    client = get_docker_client()
    image = "debian@sha256:427752aa7da803378f765f5a8efba421df5925cbde8ab011717f3642f406fb15"
    container = client.containers.run(
        image, detach=True, tty=True, security_opt=['seccomp:unconfined'])
    try:
        minimizer = ReproZipMinimizer(
            container.id, commands, packfile_save_dir=dir)
        packfile_path = minimizer.run()
    except Exception:
        raise
    finally:
        container.stop()
        container.remove()
    return packfile_path


def test_merge_pack_files():
    tmpdir = tempfile.mkdtemp()

    cmd = ["du --help", "ls --help"]
    packpath = _create_packfile(cmd, tmpdir)
    new_name = "first-pack.rpz"
    os.rename(packpath, os.path.join(tmpdir, new_name))

    cmd = ["ls -l /", "grep --help"]
    _create_packfile(cmd, tmpdir)

    pattern = os.path.join(tmpdir, '*.rpz')
    packfiles = glob(pattern)
    assert packfiles, "packfiles not found"

    outfile = os.path.join(tmpdir, 'merged.rpz')
    merge_pack_files(outfile=outfile, packfiles=packfiles)

    with tarfile.open(outfile) as tar:
        tar.extractall(path=tmpdir)
        datafile = os.path.join(tmpdir, 'DATA.tar.gz')
        with tarfile.open(datafile) as tardata:
            tardata.extractall(path=tmpdir)
            usr_bin_path = os.path.join(tmpdir, 'DATA', 'usr', 'bin')
            bin_path = os.path.join(tmpdir, 'DATA', 'bin')
            print("/usr/bin ::", os.listdir(usr_bin_path))
            print("/bin ::", os.listdir(bin_path))

            assert os.path.isfile(os.path.join(usr_bin_path, 'du'))
            assert os.path.isfile(os.path.join(bin_path, 'grep'))
            assert os.path.isfile(os.path.join(bin_path, 'ls'))
            assert not os.path.isfile(os.path.join(bin_path, 'rm'))
            assert not os.path.isfile(os.path.join(bin_path, 'sed'))
            assert not os.path.isfile(os.path.join(bin_path, 'tar'))
