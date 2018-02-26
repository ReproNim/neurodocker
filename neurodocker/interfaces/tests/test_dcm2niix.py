"""Tests for neurodocker.interfaces.dcm2niix"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces.tests import utils


class TestDcm2niix(object):
    """Tests for ANTs class."""

    def test_build_image_dcm2niix_master_source_centos7(self):
        """Install dcm2niix from source on CentOS 7."""
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('dcm2niix', {'version': 'master', 'method': 'source'}),
                ('user', 'neuro'),
            ],
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='dcm2niix-master_centos7',
        )

        cmd = "bash /testscripts/test_dcm2niix.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('dcm2niix', {'version': 'master', 'method': 'source'}),
                ('user', 'neuro'),
            ],
        }

        assert SingularityRecipe(specs).render()
