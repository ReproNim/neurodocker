"""Tests for neurodocker.interfaces.PETPVC"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
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
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='petpvc_xenial',
        )

        cmd = "bash /testscripts/test_petpvc.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

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
