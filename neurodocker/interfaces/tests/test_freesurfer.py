"""Tests for neurodocker.interfaces.FreeSurfer"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import FreeSurfer
from neurodocker.interfaces.tests import utils


class TestFreeSurfer(object):
    """Tests for FreeSurfer class."""

    def test_build_image_freesurfer_600_min_binaries_zesty(self):
        """Install minimized FreeSurfer binaries on Ubuntu Zesty."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'ubuntu:xenial'),
                    ('freesurfer', {'version': '6.0.0', 'use_binaries': True,
                                    'min': True}),
                    ('user', 'neuro'),
                 ]}
        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['freesurfer-min_zesty']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_freesurfer.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)

    def test_copy_license(self):
        """Test that only relative paths are accepted."""
        import os
        abspath = os.path.abspath('test.txt')
        with pytest.raises(ValueError):
            FreeSurfer('6.0.0', 'yum', license_path=abspath, check_urls=False)

        path = 'test.txt'
        fs = FreeSurfer('6.0.0', 'yum', license_path=path, check_urls=False)
        assert "COPY" in fs.cmd, "Copy instruction not found"
        assert path in fs.cmd, "Path to license not found"
        assert 'license.txt' in fs.cmd, "License file named improperly"
