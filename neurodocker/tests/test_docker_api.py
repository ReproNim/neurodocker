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
                                    DockerContainer, RawOutputLogger,
                                    require_docker)
from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM

client = docker.from_env()


def test_docker_is_running():
    assert docker_is_running(client), "Docker is not running"


class TestDockerfile(object):

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.specs = {'base': 'ubuntu:16.04',
                      'pkg_manager': 'apt',
                      'conda_env': {'python_version': '3.5.1',
                                    'conda_install': 'numpy',
                                    'pip_install': 'pandas'},
                      'software': {'ants': {'use_binaries': True, 'version': '2.1.0'}}}

        base = "FROM {}".format(self.specs['base'])
        miniconda = Miniconda(**self.specs['conda_env']).cmd
        ants = ANTs(**self.specs['software']['ants']).cmd

    def test_init(self):
        assert Dockerfile(self.specs, 'apt').cmd == self.full, "error creating Dockerfile"

    def test_save(self):
        dockerfile_path = os.path.join(self.tmpdir.strpath, 'Dockerfile')
        Dockerfile(self.specs, 'apt').save(filepath=dockerfile_path)

        assert len(self.tmpdir.listdir()) == 1, "file not saved"

        content = self.tmpdir.join("Dockerfile").read()
        assert content == self.full + "\n", "error in saved Dockerfile"


class TestRawOutputLogger(object):
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test_start(self):
        cmd = "FROM alpine:latest"
        cmd = cmd.encode('utf-8')
        cmd = BytesIO(cmd)
        logs = client.api.build(fileobj=cmd, rm=True)
        logger = RawOutputLogger(logs)
        logger.daemon = True
        logger.start()

        assert logger.is_alive(), "RawOutputLogger not alive!"

        while logger.is_alive():
            pass

        image = client.images.get(logger.id)
        assert isinstance(image, docker.models.images.Image), "image is not a Docker image!"


class TestBuildCompleteDockerImage(object):
    """Build a Docker image that includes all of the supported software.
    """
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

        self.specs = {'base': 'ubuntu:16.04',
                      'conda_env': {'python_version': '3.5.1',
                                    'conda_install': 'traits',
                                    'pip_install': 'https://github.com/nipy/nipype/archive/master.tar.gz'},
                      'software': {'ants': {'use_binaries': True, 'version': '2.1.0'},
                                   'fsl': {'use_binaries': True, 'version': '5.0.8'},
                                   #'spm': {''}
                                   }}

    def test_create_build_and_run(self):
        """Test building Docker image and running command within Docker
        container.
        """
        tag = "test:complete"

        cmd = Dockerfile(self.specs, 'apt').cmd
        print(cmd)
        cmd = cmd.encode('utf-8')
        cmd = BytesIO(cmd)

        # Build the image.
        image = DockerImage(fileobj=cmd).build_raw()

        container = DockerContainer(image)
        container.start()
        # "bash -c '$SPMMCRCMD'" should be tested, but it blocks. How do we get
        # around that?
        cmds = ["Atropos -h", "bet -h",]
        outputs = []
        for cmd in cmds:
            output = container.exec_run(cmd=cmd)
            outputs.append(output)
        container.cleanup(remove=True, force=True)

        outputs_str = ' '.join(outputs)
        assert "error:" not in outputs_str, "Error in command execution."
