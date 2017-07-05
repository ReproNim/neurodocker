"""Tests for neurodocker.dockerfile"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import pytest

from neurodocker.dockerfile import Dockerfile
from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM


class TestDockerfile(object):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.specs = {'base': 'ubuntu:17.04',
                      'pkg_manager': 'apt',
                      'check_urls': False,
                      'miniconda': {'python_version': '3.5.1',
                                    'conda_install': 'numpy',
                                    'pip_install': 'pandas'},
                      'ants': {'version': '2.1.0', 'use_binaries': True},
                      'fsl': {'version': '5.0.10', 'use_binaries': True},
                      'spm': {'version': 12, 'matlab_version': 'R2017a'},
                      'instruction': ['RUN ls', 'WORKDIR /home'],}

        self.base = "FROM {}".format(self.specs['base'])
        self.noninteractive = "ARG DEBIAN_FRONTEND=noninteractive"
        self.miniconda = Miniconda(pkg_manager='apt', check_urls=False, **self.specs['miniconda']).cmd
        self.ants = ANTs(pkg_manager='apt', check_urls=False, **self.specs['ants']).cmd
        self.fsl = FSL(pkg_manager='apt', check_urls=False, **self.specs['fsl']).cmd
        self.spm = SPM(pkg_manager='apt', check_urls=False, **self.specs['spm']).cmd

    def test___repr__(self):
        Dockerfile(self.specs)

    def test___str__(self):
        df = Dockerfile(self.specs)
        assert str(df) == df.cmd

    def test__create_cmd(self):
        cmd = Dockerfile(self.specs, 'apt')._create_cmd()
        assert self.base in cmd
        assert self.noninteractive in cmd
        assert self.miniconda in cmd
        assert self.ants in cmd
        assert self.fsl in cmd
        assert self.spm in cmd
        assert self.specs['instruction'][0] in cmd
        assert self.specs['instruction'][1] in cmd

    def test_add_base(self):
        assert "FROM" in Dockerfile(self.specs).add_base()

    def test_add_common_dependencies(self):
        cmd = Dockerfile(self.specs).add_common_dependencies()
        assert "RUN" in cmd
        assert "install" in cmd

    def test_add_miniconda(self):
        cmd = Dockerfile(self.specs).add_miniconda()
        assert "RUN" in cmd
        assert "python" in cmd

    def test_add_software(self):
        cmd = Dockerfile(self.specs).add_software()
        assert self.miniconda not in cmd
        assert self.ants in cmd
        assert self.fsl in cmd
        assert self.spm in cmd

    def test_save(self):
        filepath = self.tmpdir.join('Dockerfile')
        df = Dockerfile(self.specs)
        df.save(filepath.strpath)
        assert len(self.tmpdir.listdir()) == 1, "file not saved"
        assert df.cmd in filepath.read(), "file content not correct"
