from __future__ import absolute_import

# This has to come first because Dockerfile and SpecsParser import this dict.
from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM

SUPPORTED_SOFTWARE = {'ants': ANTs,
                      'fsl': FSL,
                      'miniconda': Miniconda,
                      'spm': SPM,
                      }

from neurodocker.docker_api import DockerContainer, Dockerfile, DockerImage
from neurodocker.parser import SpecsParser
