"""Utilities for `neurodocker.interfaces.tests`."""

import io
import logging
import os
from pathlib import Path
import posixpath
import subprocess

from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.utils import get_docker_client
from neurodocker.utils import get_singularity_client

logger = logging.getLogger(__name__)

PUSH_IMAGES = os.environ.get('ND_PUSH_IMAGES', False)
DOCKER_CACHEDIR = os.path.join(os.path.sep, 'tmp', 'cache')
# Singularity builds clear the /tmp directory
SINGULARITY_CACHEDIR = os.path.join(Path.home(), 'tmp', 'cache')

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
    refpath = os.path.join(DOCKER_CACHEDIR, "Dockerfile." + refpath)

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
        os.makedirs(os.path.dirname(refpath), exist_ok=True)
        with open(refpath, 'w') as fp:
            fp.write(df)


def test_singularity_container_from_specs(specs, bash_test_file):
    """"""
    sr_dir = "singularity_cache"
    os.makedirs(sr_dir, exist_ok=True)

    intname = bash_test_file[5:].split('.')[0]
    refpath = os.path.join(SINGULARITY_CACHEDIR, "Singularity." + intname)

    sr = SingularityRecipe(specs).render()

    if os.path.exists(refpath):
        logger.info("loading cached reference singularity spec")
        with open(refpath, 'r') as fp:
            reference = fp.read()
        if _dockerfiles_equivalent(sr, reference):
            logger.info("test equal to reference singularity spec, passing")
            return  # do not build and test because nothing has changed

    logger.info("building singularity image")
    filename = os.path.join(sr_dir,  "Singularity." + intname)
    with open(filename, 'w') as fp:
        fp.write(sr)

    client = get_singularity_client()
    img = client.build(
        recipe=filename,
        image=os.path.join(sr_dir, intname + ".sqsh"))

    bash_test_file = posixpath.join("/testscripts", bash_test_file)
    test_cmd = "bash " + bash_test_file

    # TODO(kaczmarj): replace the exec with a singularity python client
    # command.
    cmd = "singularity run --bind {s}:{d} {img} {args}"
    cmd = cmd.format(s=here, d=_volumes[here]['bind'], img=img, args=test_cmd)

    output = subprocess.check_output(cmd.split())
    passed = output.decode().endswith('passed')
    assert passed
    if passed:
        os.makedirs(os.path.dirname(refpath), exist_ok=True)
        with open(refpath, 'w') as fp:
            fp.write(sr)
    os.remove(img)


def _prune_dockerfile(string, comment_char="#"):
    """Remove comments, emptylines, and last layer (serialize to JSON)."""
    string = string.strip()  # trim white space on both ends.
    json_removed = '\n\n'.join(string.split('\n\n')[:-1])
    json_removed = "".join(json_removed.split())
    return '\n'.join(
        row for row in json_removed.split('\n') if not
        row.startswith(comment_char) and row)


def _dockerfiles_equivalent(df_a, df_b):
    """Return True if unicode strings `df_a` and `df_b` are equivalent. Does
    not consider comments or empty lines.
    """
    print(_prune_dockerfile(df_a))
    print(_prune_dockerfile(df_b))
    return _prune_dockerfile(df_a) == _prune_dockerfile(df_b)
