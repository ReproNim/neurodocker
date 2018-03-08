"""Tests for neurodocker.interfaces.AFNI"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import pytest

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
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
                ('afni', {'version': 'latest', 'method': 'binaries'}),
                ('user', 'neuro'),
            ],
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True, tag="afni")

        cmd = "bash /testscripts/test_afni.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        """Test whether Singularity recipe generation fails."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://debian:stretch'),
                ('afni', {'version': 'latest', 'method': 'binaries'}),
                ('user', 'neuro'),
            ],
        }
        assert SingularityRecipe(specs).render()

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            AFNI(version='fakeversion', pkg_manager='apt')
