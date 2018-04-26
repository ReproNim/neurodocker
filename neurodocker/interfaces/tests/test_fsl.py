"""Tests for neurodocker.interfaces.FSL"""

from neurodocker.interfaces.tests import utils


class TestFSL(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('fsl', {'version': '5.0.10'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_fsl.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('fsl', {'version': '5.0.10'}),
                ('user', 'neuro'),
            ]
        }
        bash_test_file = "test_fsl.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
