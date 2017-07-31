"""Tests for neurodocker.interfaces.SPM"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

from neurodocker.interfaces import SPM
from neurodocker.interfaces.tests import utils

class TestSPM(object):
    """Tests for SPM class."""

    def test_build_image_spm_12_standalone_centos7(self):
        """Install standalone SPM12 and MATLAB MCR R2017a."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('spm', {'version': '12', 'matlab_version': 'R2017a'}),
                    ('user', 'neuro'),
                 ]}
        container = utils.get_container_from_specs(specs)

        cmd = ["/bin/bash", "-c", """echo 'fprintf("desired output")' > /tmp/test.m """]
        container.exec_run(cmd)
        cmd = ["/bin/bash", "-c", "$SPMMCRCMD /tmp/test.m"]
        output = container.exec_run(cmd)
        assert "error" not in output.lower(), "error running SPM command"
        assert "desired output" in output, "expected output not found"
        utils.test_cleanup(container)
