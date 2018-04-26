"""Tests for neurodocker.interfaces.MINC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from neurodocker.interfaces.tests import utils


class TestMINC(object):

    def test_docker(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:xenial'),
                ('minc', {'version': '1.9.15'}),
                ('user', 'neuro'),
            ]
        }

        bash_test_file = "test_minc.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('minc', {'version': '1.9.15'}),
                ('user', 'neuro'),
            ]
        }
        bash_test_file = "test_minc.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file)
