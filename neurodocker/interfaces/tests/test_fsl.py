"""Tests for neurodocker.interfaces.FSL"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

import pytest

from neurodocker.docker_api import (client, Dockerfile, DockerImage,
                                    DockerContainer)
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import FSL


class TestFSL(object):
    """Tests for FSL class."""

    @pytest.mark.skip(reason="python installer raises KeyError")
    def test_build_image_fsl_latest_pyinstaller_centos7(self):
        """Install latest FSL with FSL's Python installer on CentOS 7."""
        specs = {'base': 'centos:7',
                 'pkg_manager': 'yum',
                 'fsl': {'version': 'latest', 'use_installer': True}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()

    def test_build_image_fsl_508_binaries_xenial(self):
        """Install FSL binaries on Ubuntu Xenial."""
        specs = {'base': 'ubuntu:xenial',
                 'pkg_manager': 'apt',
                 'fsl': {'version': '5.0.9', 'use_binaries': True}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='apt').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()
