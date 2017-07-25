"""Tests for neurodocker.interfaces.FreeSurfer"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import FreeSurfer
from neurodocker.interfaces.tests import utils

class TestFreeSurfer(object):
    """Tests for FreeSurfer class."""

    @pytest.mark.skip(reason="requirements exceed available resources")
    def test_build_image_freesurfer_600_binaries_xenial(self):
        """Install FSL binaries on Ubuntu Xenial."""
        specs = {'pkg_manager': 'apt',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'ubuntu:xenial'),
                    ('freesurfer', {'version': '6.0.0', 'use_binaries': True})
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('recon-all')
        assert "error" not in output, "error running recon-all"
        utils.test_cleanup(container)

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
