"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import pytest

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces import ANTs
from neurodocker.interfaces.tests import utils


class TestANTs(object):
    """Tests for ANTs class."""

    def test_build_image_ants_220_binaries_centos7(self):
        """Install ANTs 2.2.0 binaries on CentOS 7."""
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('ants', {'version': '2.2.0', 'method': 'binaries'}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='ants-2.0.0_stretch',
        )

        cmd = "bash /testscripts/test_ants.sh"
        assert DockerContainer(image).run(cmd, volumes=utils.volumes)

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
