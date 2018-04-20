"""Tests for neurodocker.interfaces.Miniconda"""

from neurodocker.interfaces.tests import utils


class TestMiniconda(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('user', 'neuro'),
                (
                    'miniconda',
                    {
                        'env_name': 'default',
                        'conda_install': ['python=3.6.5', 'traits'],
                        'pip_install': ['nipype'],
                        'activate': True,
                    }
                ),
                (
                    'miniconda',
                    {
                        'env_name': 'default',
                        'pip_install': ['pylsl'],
                    }
                ),
            ],
        }

        bash_test_file = "test_miniconda.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://debian:stretch-slim'),
                ('user', 'neuro'),
                (
                    'miniconda',
                    {
                        'env_name': 'default',
                        'conda_install': ['python=3.6.5', 'traits'],
                        'pip_install': ['nipype'],
                        'activate': True,
                    }
                ),
                (
                    'miniconda',
                    {'env_name': 'default', 'pip_install': ['pylsl']}
                ),
            ],
        }

        bash_test_file = "test_miniconda.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
