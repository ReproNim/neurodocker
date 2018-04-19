"""Tests for neurodocker.interfaces.NeuroDebian"""

from neurodocker.interfaces.tests import utils


class TestNeuroDebian(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:16.04'),
                (
                    'neurodebian',
                    {
                        'os_codename': 'stretch',
                        'server': 'usa-nh',
                        'full': True,
                    }
                ),
                ('install', ['dcm2niix']),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_neurodebian.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                (
                    'neurodebian',
                    {
                        'os_codename': 'stretch',
                        'server': 'usa-nh',
                        'full': True,
                    }
                ),
                ('install', ['dcm2niix']),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_neurodebian.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
