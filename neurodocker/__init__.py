# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

from neurodocker import interfaces

SUPPORTED_SOFTWARE = {'ants': interfaces.ANTs,
                      'fsl': interfaces.FSL,
                      'miniconda': interfaces.Miniconda,
                      'mrtrix3': interfaces.MRtrix3,
                      'spm': interfaces.SPM,
                      }

from neurodocker.dockerfile import Dockerfile
from neurodocker.parser import SpecsParser

__version__ = '0.1.0.dev0'
