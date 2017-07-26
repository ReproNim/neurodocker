"""Tests for neurodocker.interfaces.FSL"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import FSL
from neurodocker.interfaces.tests import utils

class TestFSL(object):
    """Tests for FSL class."""

    @pytest.mark.skip(reason="python installer raises KeyError")
    def test_build_image_fsl_latest_pyinstaller_centos7(self):
        """Install latest FSL with FSL's Python installer on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('fsl', {'version': '5.0.10', 'use_binaries': True})
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        utils.test_cleanup(container)

    def test_build_image_fsl_509_binaries_xenial(self):
        """Install FSL binaries on Ubuntu Xenial."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'ubuntu:xenial'),
                    ('fsl', {'version': '5.0.9', 'use_binaries': True})
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('bet')
        assert "error" not in output, "error running bet"
        utils.test_cleanup(container)
