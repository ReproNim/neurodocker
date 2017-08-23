"""Utility functions for `neurodocker.interfaces.tests`."""
from __future__ import absolute_import

import logging
import os

from neurodocker import Dockerfile
from neurodocker.docker import client, DockerContainer, DockerImage
from neurodocker.interfaces.tests import memory

logger = logging.getLogger(__name__)


# DockerHub repositories cannot have capital letters in them.
DROPBOX_DOCKERHUB_MAPPING = {
    'afni-latest_stretch': ('/Dockerfile.AFNI-latest_stretch',
                            'kaczmarj/afni:latest_stretch'),

    'ants-2.0.0_stretch': ('/Dockerfile.ANTs-2.2.0_stretch',
                           'kaczmarj/ants:2.2.0_stretch'),

    'convert3d_zesty': ('/Dockerfile.Convert3D-1.0.0_zesty',
                        'kaczmarj/c3d:1.0.0_zesty'),

    'freesurfer-min_zesty': ('/Dockerfile.FreeSurfer-min_zesty',
                             'kaczmarj/freesurfer:min_zesty'),

    'fsl-5.0.9_centos7': ('/Dockerfile.FSL-5.0.9_centos7',
                          'kaczmarj/fsl:5.0.9_centos7'),

    'miniconda_centos7': ('/Dockerfile.Miniconda-latest_centos7',
                          'kaczmarj/miniconda:latest_centos7'),

    'mrtrix3_centos7': ('/Dockerfile.MRtrix3_centos7',
                        'kaczmarj/mrtrix3:centos7'),

    'neurodebian_stretch': ('/Dockerfile.NeuroDebian_stretch',
                            'kaczmarj/neurodebian:stretch'),

    'spm-12_zesty': ('/Dockerfile.SPM-12_zesty',
                     'kaczmarj/spm:12_zesty'),

    'minc_xenial': ('/Dockerfile.MINC_xenial',
                     'kaczmarj/minc:1.9.15_xenial'),

    'minc_centos7': ('/Dockerfile.MINC_centos7',
                     'kaczmarj/minc:1.9.15_centos7'),

    'petpvc_xenial': ('/Dockerfile.PETPVC_xenial',
                     'kaczmarj/petpvc:1.2.0b_xenial'),

}


here = os.path.dirname(os.path.realpath(__file__))
volumes = {here: {'bind': '/testscripts', 'mode': 'ro'}}



def pull_image(name, **kwargs):
    """Pull image from DockerHub. Return None if image is not found.

    This does not stream the raw output of the pull.

    Parameters
    ----------
    name : str
        Name of Docker image to pull. Should include repository and tag.
        Example: 'kaczmarj/neurodocker:latest'.

    """
    import docker

    try:
        return client.images.pull(name, **kwargs)
    except docker.errors.NotFound:
        return None


def build_image(df, name):
    """Build and return image.

    Parameters
    ----------
    df : str
        String representation of Dockerfile.
    name : str
        Name of Docker image to build. Should include repository and tag.
        Example: 'kaczmarj/neurodocker:latest'.
    """
    logger.info("Building image: {} ...".format(name))
    return DockerImage(df).build(log_console=True, tag=name)


def push_image(name):
    """Push image to DockerHub.

    Parameters
    ----------
    name : str
        Name of Docker image to push. Should include repository and tag.
        Example: 'kaczmarj/neurodocker:latest'.
    """
    logger.info("Pushing image to DockerHub: {} ...".format(name))
    client.images.push(name)


def _get_dbx_token():
    """Get access token for Dopbox API."""
    import os
    import warnings

    try:
        return os.environ['DROPBOX_TOKEN']
    except KeyError:
        warnings.warn("Environment variable not found: DROPBOX_TOKEN."
                      " Cannot interact with Dropbox API. Cannot compare "
                      " Dockerfiles. Will pull existing Docker images ...")
        return None


def _check_can_push():
    """Raise error if user cannot push to DockerHub."""
    pass


def get_image_from_memory(df, remote_path, name, force_build=False):
    """Return image and boolean indicating whether or not to push resulting
    image to DockerHub.
    """
    if force_build:
        logger.info("Building image (forced) ... Result should be pushed.")
        image = build_image(df, name)
        push = True
        return image, push

    token = _get_dbx_token()

    # Take into account other forks of the project. They cannot use the secret
    # environment variables in travis ci (e.g., the dropbox token).
    if token is None:
        image = pull_image(name)
        push = False
        return image, push

    dbx_client = memory.Dropbox(token)

    if memory.should_build_image(df, remote_path, remote_object=dbx_client):
        logger.info("Building image... Result should be pushed.")
        image = build_image(df, name)
        push = True
    else:
        logger.info("Attempting to pull image ...")
        image = pull_image(name)
        push = False
        if image is None:
            logger.info("Image could not be pulled. Building ..."
                        " Result should be pushed.")
            image = build_image(df, name)
            push = True
    return image, push
