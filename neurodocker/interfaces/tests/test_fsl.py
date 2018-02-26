"""Tests for neurodocker.interfaces.FSL"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces.tests import utils


class TestFSL(object):
    """Tests for FSL class."""

    def test_build_image_fsl_5010_centos7(self):
        """Install latest FSL with FSL's Python installer on CentOS 7."""
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('fsl', {'version': '5.0.10', 'eddy_5011': True}),
                ('user', 'neuro'),
            ]
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='fsl-5.0.10_centos7',
        )

        cmd = "bash /testscripts/test_fsl.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('fsl', {'version': '5.0.10', 'eddy_5011': True}),
                ('user', 'neuro'),
            ]
        }
        assert SingularityRecipe(specs).render()
