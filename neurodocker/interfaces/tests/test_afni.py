"""Tests for neurodocker.interfaces.AFNI"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces import AFNI
from neurodocker.interfaces.tests import utils


class TestAFNI(object):
    """Tests for AFNI class."""

    def test_build_image_afni_latest_binaries_stretch(self):
        """Install latest AFNI binaries on Debian stretch."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'debian:stretch'),
                ('afni', {'version': 'latest', 'use_binaries': True}),
                ('user', 'neuro'),
            ],
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='afni-latest_stretch',
        )

        cmd = "bash /testscripts/test_afni.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image)

    def test_singularity(self):
        """Test whether Singularity recipe generation fails."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://debian:stretch'),
                ('afni', {'version': 'latest', 'use_binaries': True}),
                ('user', 'neuro'),
            ],
        }
        assert SingularityRecipe(specs).render()

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            AFNI(version='fakeversion', pkg_manager='apt')
