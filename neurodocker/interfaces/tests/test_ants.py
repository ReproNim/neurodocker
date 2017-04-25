"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

from neurodocker.docker_api import (client, Dockerfile, DockerImage,
                                    DockerContainer)
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import ANTs


class TestANTs(object):
    """Tests for ANTs class."""

    def test_build_image_ants_210_binaries_centos7(self):
        """Install ANTs 2.1.0 binaries on CentOS 7."""
        specs = {'base': 'centos:7',
                 'pkg_manager': 'yum'
                 'ants': {'version': '2.1.0', 'use_binaries': True}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('Atropos')
        assert "error" not in output, "error running Atropos"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()

    def test_build_from_source_github(self):
        # TODO: expand on tests for building ANTs from source. It probably
        # will not be possible to build ANTs in Travic because of the 50 min
        # time limit. It takes about 45 minutes to compile ANTs.

        ants = ANTs(version='latest', pkg_manager='apt', use_binaries=False)
        assert ants.cmd

        ants = ANTs(version='latest', pkg_manager='yum', use_binaries=False)
        assert ants.cmd
