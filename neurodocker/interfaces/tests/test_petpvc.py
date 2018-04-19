"""Tests for neurodocker.interfaces.PETPVC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

import pytest

from neurodocker.interfaces.tests import utils


class TestPETPVC(object):
    """Tests for PETPVC class."""

    @pytest.mark.skip("petpvc not implemented yet")
    def test_docker(self):
        """Install PETPVC binaries on Ubuntu Xenial."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:xenial'),
                ('petpvc', {'version': '1.2.0-b'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_petpvc.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    @pytest.mark.skip("petpvc not implemented yet")
    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:xenial'),
                ('petpvc', {'version': '1.2.0-b'}),
                ('user', 'neuro'),
            ]
        }

        utils.test_singularity_container_from_specs(specs=specs)
