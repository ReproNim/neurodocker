"""Tests for neurodocker.interfaces.AFNI"""

import pytest

from neurodocker.interfaces import AFNI
from neurodocker.interfaces.tests import utils


class TestAFNI(object):

    def test_docker(self):
        """Install latest AFNI binaries on Debian stretch."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'debian:stretch'),
                ('afni', {'version': 'latest', 'method': 'binaries'}),
                ('user', 'neuro'),
            ],
        }

        bash_test_file = "test_afni.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://debian:stretch'),
                ('afni', {'version': 'latest', 'method': 'binaries'}),
                ('user', 'neuro'),
            ],
        }
        bash_test_file = "test_afni.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            AFNI(version='fakeversion', pkg_manager='apt')
