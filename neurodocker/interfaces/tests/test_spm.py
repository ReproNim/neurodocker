"""Tests for neurodocker.interfaces.SPM"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

import pytest

from neurodocker.docker_api import Dockerfile, DockerImage, DockerContainer
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import SPM

class TestSPM(object):
    """Tests for SPM class."""

    def test_install_centos7(self):
        """Install SPM12 and MATLAB R2017a on CentOS 7."""
        specs = {'base': 'centos:7',
                 'software': {
                     'spm': {'version': '12', 'matlab_version': 'R2017a'}}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start(working_dir='/home')

        cmd = ["/bin/sh", "-c", """echo 'fprintf("\ndesired output")' > test.m """]
        container.exec_run(cmd)
        cmd = ["/bin/sh", "-c", "$SPMMCRCMD test.m"]
        output = container.exec_run(cmd)
        assert "error" not in output.lower(), "error running SPM command"
        assert "desired output" in output, "expected output not found"
        container.cleanup(remove=True, force=True)
