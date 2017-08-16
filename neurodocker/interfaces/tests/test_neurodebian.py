"""Tests for neurodocker.interfaces.NeuroDebian"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import NeuroDebian
from neurodocker.interfaces.tests import utils


class TestNeuroDebian(object):
    """Tests for NeuroDebian class."""

    def test_build_image_neurodebian_dcm2niix_stretch(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on Debian Stretch.
        """
        specs = {'pkg_manager': 'apt',
                 'check_urls': False,
                 'instructions': [
                    ('base', 'debian:stretch'),
                    ('neurodebian', {'os_codename': 'stretch',
                                    'download_server': 'usa-nh',
                                    'full': True,
                                    'pkgs': ['dcm2niix']}),
                    ('user', 'neuro'),
                ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['neurodebian_stretch']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_neurodebian.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
