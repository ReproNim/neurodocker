"""Tests for neurodocker.interfaces.NeuroDebian"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestNeuroDebian(object):
    """Tests for NeuroDebian class."""

    def test_build_image_neurodebian_dcm2niix_xenial(self):
        """Install NeuroDebian on Ubuntu 16.04."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:16.04'),
                (
                    'neurodebian',
                    {
                        'version': 'generic',
                        'method': 'custom',
                        'os_codename': 'stretch',
                        'download_server': 'usa-nh',
                        'full': True,
                        'pkgs': ['dcm2niix']
                    }
                ),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_neurodebian.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                (
                    'neurodebian',
                    {
                        'version': 'generic',
                        'method': 'custom',
                        'os_codename': 'stretch',
                        'download_server': 'usa-nh',
                        'full': True,
                        'pkgs': ['dcm2niix']
                    }
                ),
                ('user', 'neuro'),
            ]
        }

        assert SingularityRecipe(specs).render()
