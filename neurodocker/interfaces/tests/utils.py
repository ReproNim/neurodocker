"""Utility functions for `neurodocker.interfaces.tests`."""
from __future__ import absolute_import

import logging
import os
import posixpath

from neurodocker.docker import client
from neurodocker.docker import DockerContainer
from neurodocker.docker import DockerImage
from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.interfaces.tests import memory

logger = logging.getLogger(__name__)

_NO_PUSH_IMAGES = os.environ.get('NEURODOCKERNOPUSHIMAGES', False)

here = os.path.dirname(os.path.realpath(__file__))
_volumes = {here: {'bind': '/testscripts', 'mode': 'ro'}}

_container_run_kwds = {'volumes': _volumes}

# DockerHub repositories cannot have capital letters in them.
DROPBOX_DOCKERHUB_MAPPING = {
    'afni-latest_stretch': (
        '/Dockerfile.AFNI-latest_stretch', 'kaczmarj/afni:latest_stretch'
    ),
    'ants-2.0.0_stretch': (
        '/Dockerfile.ANTs-2.2.0_stretch', 'kaczmarj/ants:2.2.0_stretch'
    ),
    'convert3d_xenial': (
        '/Dockerfile.Convert3D-1.0.0_xenial', 'kaczmarj/c3d:1.0.0_xenial'
    ),
    'dcm2niix-master_centos7': (
        '/Dockerfile.dcm2niix-master_centos7',
        'kaczmarj/dcm2niix:master_centos7'
    ),
    'freesurfer-min_xenial': (
        '/Dockerfile.FreeSurfer-min_xenial', 'kaczmarj/freesurfer:min_xenial'
    ),
    'fsl-5.0.10_centos7': (
        '/Dockerfile.FSL-5.0.10_centos7', 'kaczmarj/fsl:5.0.10_centos7'
    ),
    'matlabmcr-2010a_stretch': (
        '/Dockerfile.MatlabMCR_stretch', 'kaczmarj/matlabmcr:stretch'
    ),
    'minc_xenial': (
        '/Dockerfile.MINC_xenial', 'kaczmarj/minc:1.9.15_xenial'
    ),
    'miniconda_centos7': (
        '/Dockerfile.Miniconda-latest_centos7',
        'kaczmarj/miniconda:latest_centos7'
    ),
    'mrtrix3_centos7': (
        '/Dockerfile.MRtrix3_centos7', 'kaczmarj/mrtrix3:centos7'
    ),
    'neurodebian_stretch': (
        '/Dockerfile.NeuroDebian_stretch', 'kaczmarj/neurodebian:stretch'
    ),
    'petpvc_xenial': (
        '/Dockerfile.PETPVC_xenial', 'kaczmarj/petpvc:1.2.0b_xenial'
    ),
    'spm-12_xenial': (
        '/Dockerfile.SPM-12_xenial', 'kaczmarj/spm:12_xenial'
    ),
}


def test_docker_container_from_specs(specs, bash_test_file):
    """"""
    df = Dockerfile(specs).render()
    image = DockerImage(df).build(log_console=True)

    bash_test_file = posixpath.join("/testscripts", bash_test_file)
    test_cmd = "bash " + bash_test_file

    res = DockerContainer(image).run(test_cmd, **_container_run_kwds)
    assert res.decode().endswith('passed')


def test_singularity_container_from_specs(specs):
    assert SingularityRecipe(specs).render()


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
        warnings.warn(
            "Environment variable not found: DROPBOX_TOKEN. Cannot interact"
            " with Dropbox API. Cannot compare Dockerfiles."
        )
        return None


def _check_can_push():
    """Raise error if user cannot push to DockerHub."""
    pass


# TODO: return `push=False` if an environment variable (ND_TEST_PUSH_IMAGES)
#   is set to some false value. This will prevent pushing on PRs, which
#   should not happen because that behavior would affect other PRs.

def _get_image_from_memory(df, remote_path, name, force_build=False):
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
        logger.info("Building image... DropBox token could not be found.")
        image = build_image(df, name)
        if image is None:
            logger.info("Image not found. Building ...")
            image = build_image(df, name)
        push = False
        return image, push

    dbx_client = memory.Dropbox(token)

    if memory.should_build_image(df, remote_path, remote_object=dbx_client):
        logger.info(
            "Building image... Result should be pushed if not on master"
            " branch."
        )
        image = build_image(df, name)
        push = True
    else:
        logger.info("Attempting to pull image ...")
        image = pull_image(name)
        push = False
        if image is None:
            logger.info(
                "Image could not be pulled. Building now. Result should be"
                " pushed if on master branch."
            )
            image = build_image(df, name)
            push = True
    return image, push


def get_image_from_memory_mapping(df, mapping_key, force_build=False):
    """Calls `get_image_from_memory` but gets `remote_path` and `name` from
    the mapping defined in this module.
    """
    try:
        remote_path, name = DROPBOX_DOCKERHUB_MAPPING[mapping_key]
    except KeyError:
        raise ValueError(
            "Key '{}' is not present in the mapping.".format(mapping_key)
        )

    image, push = _get_image_from_memory(
        df=df, remote_path=remote_path, name=name, force_build=force_build
    )

    if _NO_PUSH_IMAGES:
        push = False

    return image, push
