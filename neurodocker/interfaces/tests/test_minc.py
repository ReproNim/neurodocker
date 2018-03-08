"""Tests for neurodocker.interfaces.MINC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestMINC(object):
    """Tests for MINC class."""

    def test_build_image_minc_1915_binaries_xenial(self):
        """Install MINC binaries on Ubuntu Xenial."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:xenial'),
                ('minc', {'version': '1.9.15'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_minc.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('minc', {'version': '1.9.15'}),
                ('user', 'neuro'),
            ]
        }
        assert SingularityRecipe(specs).render()
