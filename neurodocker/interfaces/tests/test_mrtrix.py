"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces import MRtrix3
from neurodocker.interfaces.tests import utils


class TestMRtrix3(object):
    """Tests for MRtrix3 class."""

    def test_build_image_mrtrix3_binaries_centos7(self):
        """Install MRtrix3 binaries on CentOS 7."""
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('mrtrix3', {'version': '3.0'}),
                ('user', 'neuro'),
            ],
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='mrtrix3_centos7',
        )

        cmd = "bash /testscripts/test_mrtrix.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('mrtrix3', {'version': '3.0'}),
                ('user', 'neuro'),
            ],
        }

        assert SingularityRecipe(specs).render()
