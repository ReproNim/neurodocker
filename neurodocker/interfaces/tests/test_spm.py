"""Tests for neurodocker.interfaces.SPM"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

from neurodocker.docker_api import (client, Dockerfile, DockerImage,
                                    DockerContainer)
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import SPM


class TestSPM(object):
    """Tests for SPM class."""

    def test_build_image_spm_12_standalone_centos7(self):
        """Install standalone SPM12 and MATLAB MCR R2017a."""
        specs = {'base': 'ubuntu:17.04',
                 'pkg_manager': 'apt',
                 'check_urls': False,
                 'spm': {'version': '12', 'matlab_version': 'R2017a'}}
        parser = SpecsParser(specs)
        cmd = Dockerfile(parser.specs).cmd

        image = DockerImage(fileobj=cmd).build_raw()
        container = DockerContainer(image)
        container.start(working_dir='/home')

        cmd = ["/bin/sh", "-c", """echo 'fprintf("desired output")' > test.m """]
        container.exec_run(cmd)
        cmd = ["/bin/sh", "-c", "$SPMMCRCMD test.m"]
        output = container.exec_run(cmd)
        assert "error" not in output.lower(), "error running SPM command"
        assert "desired output" in output, "expected output not found"
        container.cleanup(remove=True, force=True)
        client.containers.prune()
        client.images.prune()
        client.images.remove(image.id)
