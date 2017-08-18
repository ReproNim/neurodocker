"""Tests for neurodocker.interfaces.FSL"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import FSL
from neurodocker.interfaces.tests import utils


class TestFSL(object):
    """Tests for FSL class."""

    @pytest.mark.skip(reason="necessary resources exceed available")
    def test_build_image_fsl_latest_pyinstaller_centos7(self):
        """Install latest FSL with FSL's Python installer on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('fsl', {'version': '5.0.10', 'use_binaries': True}),
                    ('user', 'neuro'),
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['fsl-5.0.10_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_fsl.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)

    def test_build_image_fsl_509_binaries_centos7(self):
        """Install FSL binaries on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('fsl', {'version': '5.0.9', 'use_binaries': True})
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['fsl-5.0.9_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_fsl.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
