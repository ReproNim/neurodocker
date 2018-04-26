"""Tests for neurodocker.interfaces.AFNI"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import AFNI
from neurodocker.interfaces.tests import utils


class TestAFNI(object):
    """Tests for AFNI class."""

    def test_build_image_afni_latest_binaries_stretch(self):
        """Install latest AFNI binaries on Debian stretch."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': False,
                 'instructions': [
                    ('base', 'debian:stretch'),
                    ('afni', {'version': 'latest', 'use_binaries': True}),
                    ('user', 'neuro'),
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['afni-latest_stretch']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_afni.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            AFNI(version='fakeversion', pkg_manager='apt', check_urls=False)
