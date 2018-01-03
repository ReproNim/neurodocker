# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

from neurodocker.version import __version__

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.generators import Dockerfile, SingularityRecipe
from neurodocker.utils import set_log_level

set_log_level('info')
