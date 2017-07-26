"""Tests for neurodocker.dockerfile"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import pytest

from neurodocker.dockerfile import Dockerfile
from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM


def _get_val_in_list_of_tuple(list_of_tuple, key):
    return [v for k, v in list_of_tuple if k == key][0]


class TestDockerfile(object):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.specs = {'pkg_manager': 'apt',
                      'check_urls': False,
                      'instructions': [
                        ('base', 'ubuntu:17.04'),
                        ('miniconda', {'python_version': '3.5.1',
                                       'conda_install': 'numpy',
                                       'pip_install': 'pandas'}),
                        ('ants', {'version': '2.1.0', 'use_binaries': True}),
                        ('fsl', {'version': '5.0.10', 'use_binaries': True}),
                      ('spm', {'version': 12, 'matlab_version': 'R2017a'}),
                      ('instruction', 'RUN ls'),
                      ]
                      }


        inst = self.specs['instructions']


        self.base = "FROM {}".format(_get_val_in_list_of_tuple(inst, 'base'))
        self.noninteractive = "ARG DEBIAN_FRONTEND=noninteractive"
        self.miniconda = Miniconda(pkg_manager='apt', check_urls=False, **_get_val_in_list_of_tuple(inst, 'miniconda')).cmd
        self.ants = ANTs(pkg_manager='apt', check_urls=False, **_get_val_in_list_of_tuple(inst, 'ants')).cmd
        self.fsl = FSL(pkg_manager='apt', check_urls=False, **_get_val_in_list_of_tuple(inst, 'fsl')).cmd
        self.spm = SPM(pkg_manager='apt', check_urls=False, **_get_val_in_list_of_tuple(inst, 'spm')).cmd

    def test___repr__(self):
        Dockerfile(self.specs)

    def test___str__(self):
        df = Dockerfile(self.specs)
        assert str(df) == df.cmd

    def test__create_cmd(self):
        cmd = Dockerfile(self.specs).cmd
        assert self.base in cmd
        assert self.noninteractive in cmd
        assert self.miniconda in cmd
        assert self.ants in cmd
        assert self.fsl in cmd
        assert self.spm in cmd
        assert _get_val_in_list_of_tuple(self.specs['instructions'], 'instruction') in cmd

    def test_save(self):
        filepath = self.tmpdir.join('Dockerfile')
        df = Dockerfile(self.specs)
        df.save(filepath.strpath)
        assert len(self.tmpdir.listdir()) == 1, "file not saved"
        assert df.cmd in filepath.read(), "file content not correct"
