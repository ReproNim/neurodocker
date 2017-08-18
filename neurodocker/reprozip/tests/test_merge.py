"""Tests for merge.py."""

from __future__ import absolute_import, division, print_function

from glob import glob
import os
import tarfile
import tempfile

from neurodocker.docker import client
from neurodocker.reprozip.trace import ReproZipMinimizer
from neurodocker.reprozip.merge import merge_pack_files


def _create_packfile(commands, dir):
    """Create packfile from list `commands` in debian:stretch container."""
    container = client.containers.run('debian:stretch', detach=True, tty=True,
                                      security_opt=['seccomp:unconfined'])
    try:
        minimizer = ReproZipMinimizer(container.id, commands,
                                      packfile_save_dir=dir)
        packfile_path = minimizer.run()
    except:
        raise
    finally:
        container.stop()
        container.remove()
    return packfile_path


def test_merge_pack_files():
    tmpdir = tempfile.mkdtemp()

    cmd = ["du -sh /usr", "rm --help"]
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
            usr_path = os.path.join(tmpdir, 'DATA', 'usr', 'bin')
            assert os.path.isfile(os.path.join(usr_path, 'du'))
            assert os.path.isfile(os.path.join(usr_path, 'grep'))
            assert os.path.isfile(os.path.join(usr_path, 'ls'))
            assert os.path.isfile(os.path.join(usr_path, 'rm'))
            assert not os.path.isfile(os.path.join(usr_path, 'sed'))
            assert not os.path.isfile(os.path.join(usr_path, 'tar'))
