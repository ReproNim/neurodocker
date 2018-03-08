"""Tests for neurodocker.interfaces.dcm2niix"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
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
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_dcm2niix.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

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
