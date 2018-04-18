# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

import sys

from neurodocker.version import __version__

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.generators import Dockerfile, SingularityRecipe
from neurodocker.utils import set_log_level

if sys.version_info[0] < 3:
    raise RuntimeError(
        "Neurodocker requires Python 3. Use Neurodocker's Docker image or"
        " install Python 3.")

set_log_level('info')
