"""Tests for neurodocker.interfaces.Miniconda"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

from neurodocker.docker_api import (client, Dockerfile, DockerImage,
                                    DockerContainer)
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import Miniconda

class TestMiniconda(object):
    """Tests for Miniconda class."""

    def test_build_image_miniconda_latest_shellscript_xenial(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on Ubuntu Xenial.
        """
        specs = {'base': 'ubuntu:xenial',
                 'conda_env': {
                    'python_version': '3.5.1',
                    'conda_install': ['traits'],
                    'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz']}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='apt').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('python -V')
        assert "3.5.1" in output, "incorrect Python version"
        output = container.exec_run('import nipype')
        assert "ImportError" not in output, "nipype not installed"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()

    def test_build_image_miniconda_latest_shellscript_centos7(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on CentOS 7.
        """
        specs = {'base': 'centos:7',
                 'conda_env': {
                    'python_version': '3.5.1',
                    'conda_install': ['traits'],
                    'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz']}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('python -V')
        assert "3.5.1" in output, "incorrect Python version"
        output = container.exec_run('import nipype')
        assert "ImportError" not in output, "nipype not installed"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()
