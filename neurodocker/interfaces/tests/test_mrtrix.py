"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import MRtrix3
from neurodocker.interfaces.tests import utils


class TestMRtrix3(object):
    """Tests for MRtrix3 class."""

    def test_build_image_mrtrix3_binaries_centos7(self):
        """Install MRtrix3 binaries on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('mrtrix3', {'use_binaries': True}),
                    ('user', 'neuro'),
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['mrtrix3_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_mrtrix.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)


    def test_build_from_source(self):
        # TODO: expand on tests for building MRtrix from source.

        mrtrix = MRtrix3(pkg_manager='apt', use_binaries=False)
        assert "git checkout" not in mrtrix.cmd

        with pytest.raises(ValueError):
            MRtrix3(pkg_manager='yum', use_binaries=False)

        mrtrix = MRtrix3(pkg_manager='apt', use_binaries=False,
                         git_hash='12345')
        assert 'git checkout 12345' in mrtrix.cmd
