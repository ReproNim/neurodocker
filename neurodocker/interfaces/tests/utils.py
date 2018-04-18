"""Utility functions for `neurodocker.interfaces.tests`."""

import hashlib
import logging
import os
import posixpath

from neurodocker.docker import client
from neurodocker.docker import DockerContainer
from neurodocker.docker import DockerImage
from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe

logger = logging.getLogger(__name__)

_NO_PUSH_IMAGES = os.environ.get('NEURODOCKERNOPUSHIMAGES', False)

here = os.path.dirname(os.path.realpath(__file__))
_volumes = {here: {'bind': '/testscripts', 'mode': 'ro'}}

_container_run_kwds = {'volumes': _volumes}


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
    return True


def _prune_dockerfile(string, comment_char="#"):
    """Remove comments, emptylines, and last layer (serialize to JSON)."""
    string = string.strip()  # trim white space on both ends.
    json_removed = '\n\n'.join(string.split('\n\n')[:-1])
    return '\n'.join(
        row for row in json_removed.split('\n') if not
        row.startswith(comment_char) and row
    )


def _get_hash(bytestring):
    """Get sha256 hash of `bytestring`."""
    return hashlib.sha256(bytestring).hexdigest()


def _dockerfiles_equivalent(df_a, df_b):
    """Return True if unicode strings `df_a` and `df_b` are equivalent. Does
    not consider comments or empty lines.
    """
    df_a_clean = _prune_dockerfile(df_a)
    hash_a = _get_hash(df_a_clean.encode())

    df_b_clean = _prune_dockerfile(df_b)
    hash_b = _get_hash(df_b_clean.encode())

    print(df_a_clean)
    print(df_b_clean)

    return hash_a == hash_b
