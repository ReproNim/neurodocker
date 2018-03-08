"""Tests for neurodocker.interfaces.Miniconda"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker import (
    DockerContainer, Dockerfile, DockerImage, SingularityRecipe
)
from neurodocker.interfaces.tests import utils


class TestMiniconda(object):
    """Tests for Miniconda class."""

    def test_build_image_miniconda_latest_shellscript_centos7(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on CentOS 7.
        """
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'centos:7'),
                ('user', 'neuro'),
                (
                    'miniconda',
                    {
                        'env_name': 'default',
                        'conda_install': ['python=3.5.1', 'traits'],
                        'pip_install': ['nipype'],
                    }
                ),
                (
                    'miniconda',
                    {'env_name': 'default', 'pip_install': ['pylsl']}
                ),
            ],
        }

        df = Dockerfile(specs).render()
        image = DockerImage(df).build(log_console=True)

        cmd = "bash /testscripts/test_miniconda.sh"
        assert DockerContainer(image).run(cmd, **utils._container_run_kwds)

    def test_singularity(self):
        specs = {
            'pkg_manager': 'yum',
            'instructions': [
                ('base', 'docker://centos:7'),
                ('user', 'neuro'),
                (
                    'miniconda',
                    {
                        'env_name': 'default',
                        'conda_install': ['python=3.5.1', 'traits'],
                        'pip_install': ['nipype'],
                    }
                ),
                (
                    'miniconda',
                    {'env_name': 'default', 'pip_install': ['pylsl']}
                ),
            ],
        }

        assert SingularityRecipe(specs).render()
