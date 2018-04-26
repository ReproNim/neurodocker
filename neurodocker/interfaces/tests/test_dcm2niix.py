"""Tests for neurodocker.interfaces.Dcm2niix"""

from neurodocker.interfaces.tests import utils


class TestDcm2niix(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('dcm2niix', {'version': 'master', 'method': 'source'}),
                ('user', 'neuro'),
            ],
        }

        bash_test_file = "test_dcm2niix.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('dcm2niix', {'version': 'master', 'method': 'source'}),
                ('user', 'neuro'),
            ],
        }

        bash_test_file = "test_dcm2niix.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
