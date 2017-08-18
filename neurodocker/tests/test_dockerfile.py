"""Tests for neurodocker.dockerfile"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import pytest

from neurodocker import dockerfile as DF
from neurodocker.interfaces import (AFNI, ANTs, FreeSurfer, FSL, Miniconda,
                                    MRtrix3, SPM)


def test__add_add():
    with pytest.raises(ValueError):
        DF._add_add(['one/path'])
    with pytest.raises(ValueError):
        DF._add_add(['/absolute/path', 'not/absolute'])
    out = DF._add_add(["path/to/here", "/tmp/here"])
    assert 'ADD ["path/to/here", "/tmp/here"]' == out


def test__add_base():
    base = "debian:stretch"
    assert "FROM {}".format(base) == DF._add_base(base)


def test__add_copy():
    with pytest.raises(ValueError):
        DF._add_copy(['one/path'])
    with pytest.raises(ValueError):
        DF._add_copy(['/absolute/path', 'not/absolute'])
    out = DF._add_copy(["path/to/here", "/tmp/here"])
    assert 'COPY ["path/to/here", "/tmp/here"]' == out


def test__add_exposed_ports():
    ports = ["1234", "5678"]
    out = DF._add_exposed_ports(ports)
    assert "EXPOSE {}".format(' '.join(ports)) == out

    ports = '1234'
    out = DF._add_exposed_ports(ports)
    assert "EXPOSE {}".format(ports) == out


def test__add_entrypoint():
    entrypoint = 'bash "path/to/file"'
    truth = 'ENTRYPOINT ["bash", "\\"path/to/file\\""]'
    assert truth == DF._add_entrypoint(entrypoint)


def test__add_env_vars():
    env = {'THIS': 'THAT'}
    truth = 'ENV THIS="THAT"'
    assert truth == DF._add_env_vars(env)

    env['A'] = 'B'
    truth = ('ENV THIS="THAT" \\\n    A="B"')
    assert truth == DF._add_env_vars(env)


def test__add_install():
    pkgs = ["git", "vim"]
    out = DF._add_install(pkgs, 'apt')
    truth = 'apt-get install -yq --no-install-recommends {}'.format(' '.join(pkgs))
    assert truth in out


def test__add_workdir():
    workdir = "/home"
    truth = "WORKDIR {}".format(workdir)
    assert truth == DF._add_workdir(workdir)


def test__add_arbitrary_instruction():
    instruction = "RUN echo hello"
    assert instruction in DF._add_arbitrary_instruction(instruction)


def test_DockerfileUsers():
    inst = DF._DockerfileUsers()
    assert inst.initialized_users == ['root']
    out = inst.add('neuro')
    assert "useradd" in out and "neuro" in out
    assert inst.initialized_users == ['root', 'neuro']
    inst.clear_memory()
    assert inst.initialized_users == ['root']


def test__add_to_entrypoint():
    cmd = "export FOO=bar"
    truth = "sed -i '$i{}' $ND_ENTRYPOINT".format(cmd)
    out = DF._add_to_entrypoint(cmd, with_run=False)
    assert truth in out and "RUN" not in out
    out = DF._add_to_entrypoint(cmd, with_run=True)
    assert truth in out and "RUN" in out





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
                        ('afni', {'version': 'latest'}),
                        ('mrtrix3', {}),
                        ('miniconda', {'python_version': '3.5.1',
                                       'env_name': 'default',
                                       'conda_install': 'numpy',
                                       'pip_install': 'pandas'}),
                        ('ants', {'version': '2.1.0', 'use_binaries': True}),
                        ('freesurfer', {'version': '6.0.0', 'min': True}),
                        ('fsl', {'version': '5.0.10', 'use_binaries': True}),
                        ('spm', {'version': 12, 'matlab_version': 'R2017a'}),
                        ('instruction', "RUN ls"),
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
        DF.Dockerfile(self.specs)

    def test___str__(self):
        df = DF.Dockerfile(self.specs)
        assert str(df) == df.cmd

    def test__create_cmd(self):
        cmd = DF.Dockerfile(self.specs).cmd
        assert self.base in cmd
        assert self.noninteractive in cmd
        assert self.miniconda in cmd
        assert self.ants in cmd
        assert self.fsl in cmd
        assert self.spm in cmd
        assert _get_val_in_list_of_tuple(self.specs['instructions'], 'instruction') in cmd

    def test_save(self):
        filepath = self.tmpdir.join('Dockerfile')
        df = DF.Dockerfile(self.specs)
        df.save(filepath.strpath)
        assert len(self.tmpdir.listdir()) == 1, "file not saved"
        assert df.cmd in filepath.read(), "file content not correct"
