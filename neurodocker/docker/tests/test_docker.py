""""Tests for neurodocker.docker.docker"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from io import BytesIO
import os
import tempfile
import threading

import docker
import pytest

from neurodocker import Dockerfile
from neurodocker.docker.docker import (BuildOutputLogger, client,
                                       copy_file_from_container,
                                       copy_file_to_container,
                                       docker_is_running, DockerContainer,
                                       DockerImage)


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

        specs = {'pkg_manager': 'apt',
                 'instructions': [
                    ('base', 'debian:jessie',)],
                 }
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


def test_copy_file_from_container():
    import posixpath

    tempdir = tempfile.mkdtemp()
    container = client.containers.run('debian:stretch', detach=True, tty=True)
    try:
        filename = "newfile.txt"
        filepath = posixpath.join("", "tmp", "newfile.txt")
        container.exec_run("touch {}".format(filepath))
        assert not os.path.isfile(os.path.join(tempdir, filename))
        path = copy_file_from_container(container, filepath, tempdir)

        local_path = os.path.join(tempdir, filename)
        assert os.path.isfile(local_path)
        os.remove(local_path)
        assert not os.path.isfile(local_path)
        copy_file_from_container(container.id, filepath, tempdir)
        assert os.path.isfile(local_path)
    except:
        raise
    finally:
        container.stop()
        container.remove()


def test_copy_file_to_container():
    import posixpath

    tempdir = tempfile.mkdtemp()
    container = client.containers.run('debian:stretch', detach=True, tty=True)
    try:
        contents = "hello from outside the container\n"
        fname = 'tempfile.txt'
        path = os.path.abspath(os.path.join(tempdir, fname))
        with open(path, 'w') as f:
            f.write(contents)

        container_dir = "/tmp"
        cmd = 'ls {}'.format(container_dir)

        assert not fname.encode() in container.exec_run(cmd)
        copy_file_to_container(container.id, path, dest=container_dir)
        assert fname.encode() in container.exec_run(cmd)

        copy_file_to_container(container, path, dest=container_dir)
        assert fname.encode() in container.exec_run(cmd)
    except:
        raise
    finally:
        container.stop()
        container.remove()
