"""Tests for neurodocker.interfaces.Miniconda"""

from neurodocker.interfaces.tests import utils


class TestMiniconda(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('user', 'neuro'),
                ('workdir', '/home/neuro'),
                (
                    'miniconda',
                    {
                        'create_env': 'default',
                        'conda_install': ['python=3.6.5', 'traits'],
                        'pip_install': ['nipype'],
                        'activate': True,
                    }
                ),
                (
                    'miniconda',
                    {
                        'use_env': 'default',
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
                ('workdir', '/home/neuro'),
                (
                    'miniconda',
                    {
                        'version': '4.6.14',
                        'create_env': 'default',
                        'conda_install': ['python=3.6.5', 'traits'],
                        'pip_install': ['nipype'],
                        'activate': True,
                    }
                ),
                (
                    'miniconda',
                    {'use_env': 'default', 'pip_install': ['pylsl']}
                ),
            ],
        }

        bash_test_file = "test_miniconda.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
