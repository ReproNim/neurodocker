"""Tests for neurodocker.interfaces.ANTs"""

import pytest

from neurodocker.interfaces import ANTs
from neurodocker.interfaces.tests import utils


class TestANTs(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('ants', {'version': '2.2.0', 'method': 'binaries'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_ants.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('ants', {'version': '2.2.0'}),
                ('user', 'neuro'),
            ]
        }
        bash_test_file = "test_ants.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            ANTs(version='fakeversion', pkg_manager='apt', check_urls=False)
