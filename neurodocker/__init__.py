# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

import sys

from neurodocker.version import __version__

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.generate import Dockerfile
from neurodocker.utils import set_log_level

if sys.version_info[0] < 3:
    raise RuntimeError("Neurodocker requires Python 3. Install Python 3 or use"
                       " Neurodocker's Docker image.")

set_log_level('info')
