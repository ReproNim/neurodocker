"""Tests for neurodocker.interfaces.SPM"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import SPM
from neurodocker.interfaces.tests import utils

class TestSPM(object):
    """Tests for SPM class."""

    def test_build_image_spm_12_standalone_zesty(self):
        """Install standalone SPM12 and MATLAB MCR R2017a."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'ubuntu:zesty'),
                    ('spm', {'version': '12', 'matlab_version': 'R2017a'}),
                    ('user', 'neuro'),
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['spm-12_zesty']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_spm.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
