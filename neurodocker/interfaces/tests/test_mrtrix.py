"""Tests for neurodocker.interfaces.ANTs"""

from neurodocker.interfaces.tests import utils


class TestMRtrix3(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('mrtrix3', {'version': '3.0_RC3'}),
                ('user', 'neuro'),
            ],
        }

        bash_test_file = "test_mrtrix.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('mrtrix3', {'version': '3.0_RC2'}),
                ('user', 'neuro'),
            ],
        }

        bash_test_file = "test_mrtrix.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
