"""Tests for neurodocker.dockerfile"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import pytest

from neurodocker import generate as DF
from neurodocker.interfaces import (AFNI, ANTs, FreeSurfer, FSL, Miniconda,
                                    MRtrix3, SPM)


def test__add_add():
    with pytest.raises(ValueError):
        DF._add_add(['one/path'])
    with pytest.raises(ValueError):
        DF._add_add(['/absolute/path', 'not/absolute'])
    out = DF._add_add(["path/to/here", "/tmp/here"])
    assert 'ADD ["path/to/here", "/tmp/here"]' == out


def test__add_to_entrypoint():
    cmd = "export FOO=bar"
    truth = "sed -i '$i{}' $ND_ENTRYPOINT".format(cmd)
    out = DF._add_to_entrypoint(cmd, with_run=False)
    assert truth in out and "RUN" not in out
    out = DF._add_to_entrypoint(cmd, with_run=True)
    assert truth in out and "RUN" in out


def test__add_arg():
    args = {'FOO': 'BAR', 'BAZ': ''}
    truth = ('ARG FOO="BAR"'
             '\nARG BAZ')
    assert truth == DF._add_arg(args)


def test__add_base():
    base = "debian:stretch"
    truth = "FROM {}".format(base)
    assert  truth == DF._add_base(base)


def test__add_cmd():
    cmd = ["--arg1", "--arg2"]
    truth = 'CMD ["--arg1", "--arg2"]'
    assert truth == DF._add_cmd(cmd)


def test__add_copy():
    with pytest.raises(ValueError):
        DF._add_copy(['one/path'])
    with pytest.raises(ValueError):
        DF._add_copy(['/absolute/path', 'not/absolute'])
    out = DF._add_copy(["path/to/here", "/tmp/here"])
    assert 'COPY ["path/to/here", "/tmp/here"]' == out


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


def test__add_exposed_ports():
    ports = ["1234", "5678"]
    out = DF._add_exposed_ports(ports)
    assert "EXPOSE {}".format(' '.join(ports)) == out

    ports = '1234'
    out = DF._add_exposed_ports(ports)
    assert "EXPOSE {}".format(ports) == out


def test__add_install():
    pkgs = ["git", "vim", "flags=-q --fake-flag"]
    out = DF._add_install(pkgs, 'apt')
    assert 'apt-get install -y -q --fake-flag' in out
    assert 'git' in out
    assert 'vim' in out
    assert '--no-install-recommends' not in out


def test__add_arbitrary_instruction():
    instruction = "RUN echo hello"
    assert instruction in DF._add_arbitrary_instruction(instruction)


def test__add_label():
    labels = {"FOO": "BAR", "BAZ": "CAT"}
    truth = ('LABEL FOO="BAR" \\'
             '\n      BAZ="CAT"')
    assert truth == DF._add_label(labels)

def test_add_run():
    cmd = "apt-get update\napt-get install -y git"
    truth = ("# User-defined instruction"
             "\nRUN apt-get update \\"
             "\n    apt-get install -y git")
    assert truth == DF._add_run(cmd)


def test__add_run_bash():
    bash = 'echo "hello world" > myfile.txt'
    truth = ('# User-defined BASH instruction'
             '\nRUN bash -c "echo \\"hello world\\" > myfile.txt"')
    assert truth == DF._add_run_bash(bash)


def test__add_volume():
    volumes = ["/usr/bin", "/var"]
    truth = 'VOLUME ["/usr/bin", "/var"]'
    assert truth == DF._add_volume(volumes)

def test__add_workdir():
    workdir = "/home"
    truth = "WORKDIR {}".format(workdir)
    assert truth == DF._add_workdir(workdir)


def test_DockerfileUsers():
    inst = DF._DockerfileUsers()
    assert inst.initialized_users == ['root']
    out = inst.add('neuro')
    assert "useradd" in out and "neuro" in out
    assert inst.initialized_users == ['root', 'neuro']
    inst.clear_memory()
    assert inst.initialized_users == ['root']


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
                        ('miniconda', {'env_name': 'default',
                                       'conda_install': 'python=3.5.1 numpy',
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
        Miniconda.clear_memory()
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
        print(cmd)
        print(self.miniconda)
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


def test_build_image_from_json():
    """Test of saving JSON in Docker image and building new Docker image with
    that JSON file.
    """
    from contextlib import redirect_stdout
    import io
    import os
    import subprocess
    import sys
    import tempfile

    from neurodocker.interfaces.tests.memory import _dockerfiles_equivalent
    from neurodocker.neurodocker import main


    def _get_dockerfile_from_stdout(args):
        f = io.StringIO()
        with redirect_stdout(f):
            main(args)
        return f.getvalue()

    # Build Docker image.
    args = ['generate', '--base', 'debian:stretch', '--pkg-manager', 'apt',
            '--install', 'vim', '--run-bash', 'echo "foo\n\'bar(baz)\'"']
    df = _get_dockerfile_from_stdout(args)
    docker_args = "docker build -t json-original -".split()
    subprocess.run(docker_args, input=df.encode(), check=True)

    # Copy JSON file onto host.
    tempdir = tempfile.mkdtemp(dir='/tmp')
    json_file = "/neurodocker/neurodocker_specs.json"
    copy_cmd = ("docker run --rm -v {}:/nd json-original mv {} /nd"
                "".format(tempdir, json_file)).split()
    subprocess.run(copy_cmd, check=True)
    json_file = os.path.join(tempdir, 'neurodocker_specs.json')

    # Create new Dockerfile and build.
    args = "generate --file {}".format(json_file).split()
    df_new = _get_dockerfile_from_stdout(args)
    docker_args = "docker build -t json-copy -".split()
    subprocess.run(docker_args, input=df_new.encode(), check=True)

    for line_a, line_b in zip(df.split('\n'), df_new.split('\n')):
        if not line_a == line_b:
            print(line_a + "\t|\t" + line_b)

    os.path.join(tempdir, "DOCKERFILE_A")
    with open(os.path.join(tempdir, "DOCKERFILE_A"), 'w') as fp:
        fp.write(df)
    with open(os.path.join(tempdir, "DOCKERFILE_B"), 'w') as fp:
        fp.write(df_new)

    assert _dockerfiles_equivalent(df, df_new), "Failed building from JSON"
