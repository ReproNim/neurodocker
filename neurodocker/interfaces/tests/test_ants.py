"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import ANTs
from neurodocker.interfaces.tests import utils


class TestANTs(object):
    """Tests for ANTs class."""

    def test_build_image_ants_210_binaries_centos7(self):
        """Install ANTs 2.1.0 binaries on CentOS 7."""
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('ants', {'version': '2.2.0', 'use_binaries': True}),
                    ('user', 'neuro'),
                 ]}
        container = utils.get_container_from_specs(specs)
        output = container.exec_run('Atropos')
        assert "error" not in output, "error running Atropos"
        utils.test_cleanup(container)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            ANTs(version='fakeversion', pkg_manager='apt', check_urls=False)

    def test_build_from_source_github(self):
        # TODO: expand on tests for building ANTs from source. It probably
        # will not be possible to build ANTs in Travic because of the 50 min
        # time limit. It takes about 45 minutes to compile ANTs.

        ants = ANTs(version='latest', pkg_manager='apt', use_binaries=False)
        assert "git checkout" not in ants.cmd

        ants = ANTs(version='2.2.0', pkg_manager='yum', use_binaries=False)
        assert ants.cmd

        ants = ANTs(version='arbitrary', pkg_manager='apt', use_binaries=False,
                    git_hash='12345')
        assert 'git checkout 12345' in ants.cmd
