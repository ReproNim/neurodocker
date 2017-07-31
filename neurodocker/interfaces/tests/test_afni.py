"""Tests for neurodocker.interfaces.AFNI"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import AFNI
from neurodocker.interfaces.tests import utils


class TestAFNI(object):
    """Tests for AFNI class."""

    def test_build_image_afni_latest_binaries_stretch(self):
        """Install latest AFNI binaries on Debian stretch."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'debian:stretch'),
                    ('afni', {'version': 'latest', 'use_binaries': True}),
                    ('user', 'neuro'),
                 ]}

        container = utils.get_container_from_specs(specs)
        output = container.exec_run('3dSkullStrip')
        assert "error" not in output, "error running 3dSkullStrip"
        utils.test_cleanup(container)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            AFNI(version='fakeversion', pkg_manager='apt', check_urls=False)
