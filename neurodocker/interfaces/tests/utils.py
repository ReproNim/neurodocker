"""Utilities for `neurodocker.interfaces.tests`."""

import hashlib
import io
import logging
import os
import posixpath

try:
    import docker
except ImportError:
    raise ImportError(
        "the docker python package is required to run interface tests")

from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe

client = docker.from_env()

logger = logging.getLogger(__name__)

PUSH_IMAGES = os.environ.get('ND_PUSH_IMAGES', False)

here = os.path.dirname(os.path.realpath(__file__))
_volumes = {here: {'bind': '/testscripts', 'mode': 'ro'}}

_container_run_kwds = {'volumes': _volumes}


def docker_is_running(client):
    """Return true if Docker server is responsive.

    Parameters
    ----------
    client : docker.client.DockerClient
        The Docker client. E.g., `client = docker.from_env()`.

    Returns
    -------
    running : bool
        True if Docker server is responsive.
    """
    try:
        client.ping()
        return True
    except Exception:
        return False


def test_docker_container_from_specs(specs, bash_test_file):
    """"""
    docker_is_running(client)

    df = Dockerfile(specs).render()
    image, build_logs = client.images.build(
        fileobj=io.BytesIO(df.encode()), rm=True)

    bash_test_file = posixpath.join("/testscripts", bash_test_file)
    test_cmd = "bash " + bash_test_file

    res = client.containers.run(image, test_cmd, **_container_run_kwds)
    assert res.decode().endswith('passed')


def test_singularity_container_from_specs(specs):
    assert SingularityRecipe(specs).render()


def push_image(image):
    """Push image to DockerHub.

    Parameters
    ----------
    image : str
        Name of Docker image to push. Should include repository and tag.
        Example: 'kaczmarj/neurodocker:latest'.
    """
    logger.info("Pushing image to DockerHub: {} ...".format(image))
    client.images.push(image)
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
