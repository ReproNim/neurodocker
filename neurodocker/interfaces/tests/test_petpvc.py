"""Tests for neurodocker.interfaces.PETPVC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

import pytest

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestPETPVC(object):
    """Tests for PETPVC class."""

    @pytest.mark.skip("petpvc not implemented yet")
    def test_build_image_petpvc_120b_binaries_xenial(self):
        """Install PETPVC binaries on Ubuntu Xenial."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:xenial'),
                ('petpvc', {'version': '1.2.0-b'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_petpvc.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    @pytest.mark.skip("petpvc not implemented yet")
    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:xenial'),
                ('petpvc', {'version': '1.2.0-b'}),
                ('user', 'neuro'),
            ]
        }

        assert SingularityRecipe(specs).render()
