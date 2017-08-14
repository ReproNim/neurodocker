# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

import logging
import sys

LOG_FORMAT = '[NEURODOCKER %(asctime)s %(levelname)s]: %(message)s'
logging.basicConfig(stream=sys.stdout, datefmt='%H:%M:%S', level=logging.INFO,
                    format=LOG_FORMAT)

from neurodocker.version import __version__

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.dockerfile import Dockerfile
