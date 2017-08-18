"""Tests for neurodocker.interfaces.Convert3D"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import Convert3D
from neurodocker.interfaces.tests import utils


class TestConvert3D(object):
    """Tests for Convert3D class."""

    def test_build_image_convert3d_100_binaries_zesty(self):
        """Install Convert3D binaries on Ubuntu Zesty."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'ubuntu:zesty'),
                    ('c3d', {'version': '1.0.0'}),
                    ('user', 'neuro'),
                 ]}
        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['convert3d_zesty']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_convert3d.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
