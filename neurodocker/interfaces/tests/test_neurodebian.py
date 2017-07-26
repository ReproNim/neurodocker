"""Tests for neurodocker.interfaces.NeuroDebian"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.interfaces import NeuroDebian
from neurodocker.interfaces.tests import utils

class TestNeuroDebian(object):
    """Tests for NeuroDebian class."""

    def test_build_image_neurodebian_dcm2niix_xenial(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on Ubuntu Xenial.
        """
        specs = {'pkg_manager': 'apt',
                 'check_urls': False,
                 'instructions': [
                    ('base', 'ubuntu:xenial'),
                    ('neurodebian', {'os_codename': 'xenial',
                                    'download_server': 'usa-nh',
                                    'full': False,
                                    'pkgs': ['dcm2niix']})
                ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('dcm2niix -h')
        assert "usage: dcm2niix" in output, "dcm2niix not working"
        utils.test_cleanup(container)
