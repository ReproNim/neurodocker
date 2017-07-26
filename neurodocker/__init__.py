# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import logging
import sys

LOG_FORMAT = '[NEURODOCKER %(asctime)s %(levelname)s]: %(message)s'
logging.basicConfig(stream=sys.stdout, datefmt='%H:%M:%S', level=logging.INFO,
                    format=LOG_FORMAT)

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.dockerfile import Dockerfile


def _get_version():
    """Return version string."""
    import os

    BASE_PATH = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(BASE_PATH, "VERSION"), 'r') as fp:
        return fp.read().strip()

__version__ = _get_version()
