"""Tests for neurodocker.interfaces.FreeSurfer"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
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
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='freesurfer-min_xenial',
        )

        cmd = "bash /testscripts/test_freesurfer.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image)

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
