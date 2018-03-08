"""Tests for neurodocker.interfaces.FreeSurfer"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestFreeSurfer(object):
    """Tests for FreeSurfer class."""

    def test_build_image_freesurfer_600_min_binaries_xenial(self):
        """Install minimized FreeSurfer binaries on Ubuntu Xenial."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:16.04'),
                ('freesurfer', {'version': '6.0.0-min'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_freesurfer.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                ('freesurfer', {'version': '6.0.0-min'}),
                ('user', 'neuro'),
            ]
        }
        assert SingularityRecipe(specs).render()
