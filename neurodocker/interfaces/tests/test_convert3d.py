"""Tests for neurodocker.interfaces.Convert3D"""

from neurodocker.interfaces.tests import utils


class TestConvert3D(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:18.04'),
                ('convert3d', {'version': '1.0.0'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_convert3d.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                ('convert3d', {'version': '1.0.0'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_convert3d.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
