"""Tests for neurodocker.interfaces.SPM"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

from neurodocker import DockerContainer, Dockerfile, SingularityRecipe
from neurodocker.interfaces.tests import utils


class TestSPM(object):
    """Tests for SPM class."""

    def test_build_image_spm_12_standalone_zesty(self):
        """Install standalone SPM12 and MATLAB MCR R2017a."""
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'ubuntu:16.04'),
                ('spm12', {'version': 'r7219', 'matlab_version': 'R2017a'}),
                ('user', 'neuro'),
            ],
        }

        df = Dockerfile(specs).render()
        image, push = utils.get_image_from_memory_mapping(
            df=df, mapping_key='spm-12_xenial',
        )

        cmd = "bash /testscripts/test_spm.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

        if push:
            utils.push_image(image)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'apt',
            'instructions': [
                ('base', 'docker://ubuntu:16.04'),
                ('spm12', {'version': 'r7219', 'matlab_version': 'R2017a'}),
                ('user', 'neuro'),
            ],
        }

        assert SingularityRecipe(specs).render()
