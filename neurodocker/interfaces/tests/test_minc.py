"""Tests for neurodocker.interfaces.MINC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import minc
from neurodocker.interfaces.tests import utils


class TestMINC(object):
    """Tests for MINC class."""

    def test_build_image_minc_1915_binaries_xenial(self):
        """Install MINC binaries on Ubuntu Xenial."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                     ('base', 'ubuntu:xenial'),
                     ('minc', {'version': '1.9.15', 'use_binaries': True, 'distro':'ubuntu'}),
                     ('user', 'neuro'),
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('bash -c "mincresample"')
        assert "error" not in output, "error running mincresample"
        utils.test_cleanup(container)

    def test_build_image_minc_1915_binaries_centos(self):
        """Install MINC binaries on Ubuntu Xenial."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                     ('base', 'centos:latest'),
                     ('minc', {'version': '1.9.15', 'use_binaries': True, 'distro':'centos'}),
                     ('user', 'neuro'),
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('bash -c "mincresample"')
        assert "error" not in output, "error running mincresample"
        utils.test_cleanup(container)