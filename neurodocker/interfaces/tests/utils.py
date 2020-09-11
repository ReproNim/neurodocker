"""Utilities for `neurodocker.interfaces.tests`."""

from distutils.spawn import find_executable
import io
import logging
import os
from pathlib import Path
import subprocess
import tempfile

from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.utils import get_docker_client

logger = logging.getLogger(__name__)

# Where to cache Dockerfiles and Singularity recipes.
CACHE_DIR = os.environ.get("NEURODOCKER_CACHE_DIR", None)
if CACHE_DIR is None:
    CACHE_DIR = Path(tempfile.gettempdir()) / "neurodocker-test-cache"
else:
    CACHE_DIR = Path(CACHE_DIR)

logger.info("caching to {}".format(CACHE_DIR))

here = os.path.dirname(os.path.realpath(__file__))
_volumes = {here: {"bind": "/testscripts", "mode": "ro"}}

_container_run_kwds = {"volumes": _volumes, "stderr": True}


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

    refpath = bash_test_file[5:].split(".")[0]
    refpath = CACHE_DIR / ("Dockerfile." + refpath)

    if refpath.exists():
        logger.info("loading cached reference dockerfile")
        reference = refpath.read_text()
        if _dockerfiles_equivalent(df, reference):
            logger.info("test equal to reference dockerfile, passing")
            return  # do not build and test because nothing has changed
    else:
        logger.info("cached reference dockerfile not found")

    logger.info("building docker image")
    image, build_logs = client.images.build(fileobj=io.BytesIO(df.encode()), rm=True)

    bash_test_file = "/testscripts/{}".format(bash_test_file)
    test_cmd = "bash " + bash_test_file
    res = client.containers.run(image, test_cmd, **_container_run_kwds)
    print("OUTPUT")
    print(res.decode().strip())
    passed = res.decode().strip().endswith("passed")
    print("VALUE OF passed =", passed)
    assert passed
    if passed:
        refpath.parent.mkdir(parents=True, exist_ok=True)
        refpath.write_text(df)
        logger.info("saving dockerfile to cache")


def test_singularity_container_from_specs(specs, bash_test_file):
    """"""
    sr_dir = Path("singularity_cache")
    sr_dir.mkdir(exist_ok=True)

    intname = bash_test_file[5:].split(".")[0]
    refpath = CACHE_DIR / ("Singularity." + intname)

    sr = SingularityRecipe(specs).render()

    if refpath.exists():
        logger.info("loading cached reference singularity recipe")
        reference = refpath.read_text()
        if _dockerfiles_equivalent(sr, reference):
            logger.info("test equal to reference singularity spec, passing")
            return  # do not build and test because nothing has changed
    else:
        logger.info("cached reference singularity recipe not found")

    logger.info("building singularity image")
    filename = sr_dir / ("Singularity." + intname)
    filename.write_text(sr)

    # Build singularity image.
    singularity_executable = find_executable("singularity")
    img = sr_dir / "{}.sif".format(intname)
    cmd = "sudo {} build {} {}.sif".format(singularity_executable, filename, img)
    subprocess.check_output(cmd.split())

    bash_test_file = "/testscripts/{}".format(bash_test_file)
    test_cmd = "bash " + bash_test_file
    cmd = "singularity run --bind {s}:{d} {img} {args}"
    cmd = cmd.format(s=here, d=_volumes[here]["bind"], img=img, args=test_cmd)
    output = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
    passed = output.decode().strip().endswith("passed")
    assert passed
    if passed:
        refpath.parent.mkdir(parents=True, exist_ok=True)
        refpath.write_text(sr)
        logger.info("saving singularity recipe to cache")
    os.remove(img)


def _prune_dockerfile(string, comment_char="#"):
    """Remove comments, emptylines, and last layer (serialize to JSON)."""
    string = string.strip()  # trim white space on both ends.
    json_removed = "\n\n".join(string.split("\n\n")[:-1])
    json_removed = "".join(json_removed.split())
    return "\n".join(
        row
        for row in json_removed.split("\n")
        if not row.startswith(comment_char) and row
    )


def _dockerfiles_equivalent(df_a, df_b):
    """Return True if unicode strings `df_a` and `df_b` are equivalent. Does
    not consider comments or empty lines.
    """
    print(_prune_dockerfile(df_a))
    print(_prune_dockerfile(df_b))
    return _prune_dockerfile(df_a) == _prune_dockerfile(df_b)
