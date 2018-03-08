"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
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
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_mrtrix.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

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
