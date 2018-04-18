"""Utilities for `neurodocker.interfaces.tests`."""

import hashlib
import io
import logging
import os
import posixpath

from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.utils import get_docker_client

logger = logging.getLogger(__name__)

PUSH_IMAGES = os.environ.get('ND_PUSH_IMAGES', False)
CACHE_LOCATION = os.path.join(os.path.sep, 'tmp', 'cache')

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
    client = get_docker_client()
    docker_is_running(client)

    df = Dockerfile(specs).render()

    refpath = bash_test_file[5:].split('.')[0]
    refpath = os.path.join(CACHE_LOCATION, "Dockerfile." + refpath)

    if os.path.exists(refpath):
        logger.info("loading cached reference dockerfile")
        with open(refpath, 'r') as fp:
            reference = fp.read()
        if _dockerfiles_equivalent(df, reference):
            logger.info("test equal to reference dockerfile, passing")
            return  # do not build and test because nothing has changed

    logger.info("building docker image")
    image, build_logs = client.images.build(
        fileobj=io.BytesIO(df.encode()), rm=True)

    bash_test_file = posixpath.join("/testscripts", bash_test_file)
    test_cmd = "bash " + bash_test_file

    res = client.containers.run(image, test_cmd, **_container_run_kwds)
    passed = res.decode().endswith('passed')
    assert passed

    if passed:
        with open(refpath, 'w') as fp:
            fp.write(df)


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
    client = get_docker_client()
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
    return _prune_dockerfile(df_a) == _prune_dockerfile(df_b)
