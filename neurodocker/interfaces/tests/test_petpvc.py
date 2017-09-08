"""Tests for neurodocker.interfaces.PETPVC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import petpvc
from neurodocker.interfaces.tests import utils


class TestPETPVC(object):
    """Tests for PETPVC class."""

    def test_build_image_petpvc_120b_binaries_xenial(self):
        """Install PETPVC binaries on Ubuntu Xenial."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                     ('base', 'ubuntu:xenial'),
                     ('petpvc', {'version': '1.2.0-b', 'use_binaries': True}),
                     ('user', 'neuro'),
                 ]}
        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['petpvc_xenial']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_petpvc.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)