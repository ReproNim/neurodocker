from __future__ import absolute_import

# This has to come first because Dockerfile and SpecsParser import it.
from neurodocker.interfaces import ANTs, FSL, SPM
SUPPORTED_NI_SOFTWARE = {'ants': ANTs,
                         'fsl': FSL,
                         'spm': SPM,
                         }

from neurodocker.docker_api import DockerContainer, Dockerfile, DockerImage
from neurodocker.parser import SpecsParser
