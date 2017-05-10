# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

from neurodocker.interfaces import ANTs, FSL, Miniconda, SPM

SUPPORTED_SOFTWARE = {'ants': ANTs,
                      'fsl': FSL,
                      'miniconda': Miniconda,
                      'spm': SPM,
                      }

from neurodocker.dockerfile import Dockerfile
from neurodocker.parser import SpecsParser

try:
    import neurodocker.docker
except ImportError:
    pass

__version__ = '0.1.0.dev0'
