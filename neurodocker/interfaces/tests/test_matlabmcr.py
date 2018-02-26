"""Tests for neurodocker.interfaces.MatlabMCR"""

import pytest

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces import ANTs
from neurodocker.interfaces.tests import utils


class TestMatlabMCR:
    """Tests for ANTs class."""

    def test_build_image_matlabmcr2010a_binaries_stretch(self):
        """Install MatlabMCR R2010a on Debian Stretch."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'debian:stretch'),
                ('ants', {'version': '2010a', 'method': 'binaries'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='matlabmcr-2010a_stretch',
        )

        # cmd = "bash /testscripts/test_ants.sh"
        # assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

    def test_invalid_binaries(self):
        with pytest.raises(ValueError):
            ANTs(version='fakeversion', pkg_manager='apt', check_urls=False)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('ants', {'version': '2.2.0'}),
                ('user', 'neuro'),
            ]
        }

        assert SingularityRecipe(specs).render()
