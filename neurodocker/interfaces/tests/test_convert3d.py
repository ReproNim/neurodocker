"""Tests for neurodocker.interfaces.Convert3D"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestConvert3D(object):
    """Tests for Convert3D class."""

    def test_build_image_convert3d_100_binaries_zesty(self):
        """Install Convert3D binaries on Ubuntu Zesty."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:18.04'),
                ('convert3d', {'version': '1.0.0'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_convert3d.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                ('convert3d', {'version': '1.0.0'}),
                ('user', 'neuro'),
            ]
        }
        assert SingularityRecipe(specs).render()
