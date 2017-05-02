"""Tests for neurodocker.docker_api"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import
from io import BytesIO
import os
import threading
import time

import docker
import pytest

from neurodocker.docker_api import (docker_is_running, Dockerfile, DockerImage,
                                    DockerContainer, BuildOutputLogger,
                                    require_docker)
from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM

client = docker.from_env()


def test_docker_is_running():
    assert docker_is_running(client), "Docker is not running"


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
                      'spm': {'version': 12, 'matlab_version': 'R2017a'},}

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

        with pytest.raises(Exception):
            df = Dockerfile(self.specs)
            df.cmd = ""
            df.save(filepath.strpath)


class TestBuildOutputLogger(object):
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.filepath = self.tmpdir.join("test.log")
        self.cmd = "FROM alpine:latest"
        self.fileobj = BytesIO(self.cmd.encode('utf-8'))

    def test_start(self):
        logs = client.api.build(fileobj=self.fileobj, rm=True)
        logger = BuildOutputLogger(logs, console=False, filepath=self.filepath.strpath)
        logger.daemon = True
        logger.start()
        assert logger.is_alive(), "BuildOutputLogger not alive"

        while logger.is_alive():
            pass
        assert self.filepath.read(), "log file empty"

    def test_get_logs(self):
        logs = client.api.build(fileobj=self.fileobj, rm=True)
        logger = BuildOutputLogger(logs, console=True)
        logger.daemon = True
        logger.start()

        while logger.is_alive():
            pass
        assert logger.logs


class TestDockerImage(object):

    def test___init__(self):
        with pytest.raises(TypeError):
            DockerImage(dict())

        specs = {'base': 'debian:jessie',
                 'pkg_manager': 'apt'}
        df = Dockerfile(specs=specs)
        # Test that fileobj is a file object.
        image = DockerImage(df)
        assert image.fileobj.read()

    def test_build(self):
        # Correct instructions.
        cmd = "FROM alpine:latest"
        image = DockerImage(cmd).build()
        assert isinstance(image, docker.models.images.Image)

        # Incorrect instructions
        cmd = "FROM ubuntu:fake_version_12345"
        with pytest.raises(docker.errors.BuildError):
            img = DockerImage(cmd).build()


class TestDockerContainer(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.image = DockerImage('FROM ubuntu:17.04').build()

    def test_start_cleanup(self):
        pre = client.containers.list()
        container = DockerContainer(self.image).start()
        post = client.containers.list()
        assert len(pre) + 1 == len(post), "container not started"

        container.cleanup(remove=True, force=True)
        assert len(pre) == len(client.containers.list()), "container not removed"

    def test_exec_run(self):
        container = DockerContainer(self.image).start()
        assert "usr" in container.exec_run("ls /")
        assert "hello" in container.exec_run('echo hello')
        container.cleanup(remove=True, force=True)

    def test_cleanup(self):
        pre = client.containers.list(all=True)
        container = DockerContainer(self.image).start(remove=False)
        assert len(pre) + 1 == len(client.containers.list(all=True))
        container.cleanup(remove=False)
        assert len(pre) + 1 == len(client.containers.list(all=True))
        container.cleanup(remove=True, force=True)
        assert len(pre) == len(client.containers.list(all=True))
