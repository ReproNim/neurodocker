"""Tests for neurodocker.interfaces.FSL"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

import pytest

from neurodocker.docker_api import Dockerfile, DockerImage, DockerContainer
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import FSL


class TestFSL(object):
    """Tests for FSL class."""

    def test_install_centos7_pyinstaller(self):
        """Install latest FSL on CentOS 7 with FSL's Python installer."""
        specs = {'base': 'centos:7',
                 'software': {
                     'fsl': {'version': 'latest', 'use_installer': True}}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)

    def test_install_debian_neurodebian(self):
        """Install FSL on Debian with NeuroDebian."""
        specs = {'base': 'debian:jessie',
                 'software': {
                     'fsl': {'version': '5.0.8', 'use_neurodebian': True}}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='apt').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)

    def test_install_ubuntu_binaries(self):
        """Install FSL binaries on Ubuntu."""
        specs = {'base': 'ubuntu:16.04',
                 'software': {
                     'fsl': {'version': '5.0.8', 'use_binaries': True}}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='apt').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)
