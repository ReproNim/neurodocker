"""Tests for neurodocker.interfaces.dcm2niix"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces.tests import utils


class TestDcm2niix(object):
    """Tests for ANTs class."""

    def test_build_image_dcm2niix_master_source_centos7(self):
        """Install dcm2niix from source on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                     ('base', 'centos:7'),
                     ('dcm2niix', {'version': 'master'}),
                     ('user', 'neuro'),
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['dcm2niix-master_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_dcm2niix.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
