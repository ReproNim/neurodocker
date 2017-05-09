""""Tests for neurodocker.docker.docker"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import
from io import BytesIO
import os
import threading
import time

import docker
import pytest

from neurodocker import Dockerfile
from neurodocker.docker.docker import (BuildOutputLogger, docker_is_running,
                                       DockerContainer, DockerImage)


client = docker.from_env()


def test_docker_is_running():
    assert docker_is_running(client), "Docker is not running"


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
        logger.start()
        living = logger.is_alive()
        assert living, "BuildOutputLogger not alive"

        while logger.is_alive():
            pass
        content = self.filepath.read()
        assert content, "log file empty"

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
        correct_type = isinstance(image, docker.models.images.Image)
        assert correct_type

        # Incorrect instructions
        cmd = "FROM ubuntu:fake_version_12345"
        with pytest.raises(docker.errors.BuildError):
            DockerImage(cmd).build()


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
