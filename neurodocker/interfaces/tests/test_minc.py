"""Tests for neurodocker.interfaces.MINC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
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
        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['minc_xenial']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_minc.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)

    def test_build_image_minc_1915_binaries_centos(self):
        """Install MINC binaries on CentOS."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                     ('base', 'centos:latest'),
                     ('minc', {'version': '1.9.15', 'use_binaries': True, 'distro':'centos'}),
                     ('user', 'neuro'),
                 ]}
        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['minc_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_minc.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)