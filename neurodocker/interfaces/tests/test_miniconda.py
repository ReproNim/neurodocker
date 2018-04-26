"""Tests for neurodocker.interfaces.Miniconda"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

import pytest

from neurodocker import DockerContainer, Dockerfile
from neurodocker.interfaces import Miniconda
from neurodocker.interfaces.tests import utils

class TestMiniconda(object):
    """Tests for Miniconda class."""

    def test_build_image_miniconda_latest_shellscript_centos7(self):
        """Install latest version of Miniconda via ContinuumIO's installer
        script on CentOS 7.
        """
        specs = {'pkg_manager': 'yum',
                 'check_urls': True,
                 'instructions': [
                    ('base', 'centos:7'),
                    ('user', 'neuro'),
                    ('miniconda', {
                        'env_name': 'default',
                        'conda_install': ['python=3.5.1', 'traits'],
                        'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz'],
                    }),
                    ('miniconda', {
                        'env_name': 'default',
                        'pip_install': ['pylsl'],
                    })
                 ]}

        df = Dockerfile(specs).cmd
        dbx_path, image_name = utils.DROPBOX_DOCKERHUB_MAPPING['miniconda_centos7']
        image, push = utils.get_image_from_memory(df, dbx_path, image_name)

        cmd = "bash /testscripts/test_miniconda.sh"
        DockerContainer(image).run(cmd, volumes=utils.volumes)

        if push:
            utils.push_image(image_name)
