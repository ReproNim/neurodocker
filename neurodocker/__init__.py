# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import

import logging
import sys

LOG_FORMAT = '[NEURODOCKER %(asctime)s %(levelname)s]: %(message)s'
logging.basicConfig(stream=sys.stdout, datefmt='%H:%M:%S', level=logging.INFO,
                    format=LOG_FORMAT)


from neurodocker import interfaces

SUPPORTED_SOFTWARE = {'afni': interfaces.AFNI,
                      'ants': interfaces.ANTs,
                      'freesurfer': interfaces.FreeSurfer,
                      'fsl': interfaces.FSL,
                      'miniconda': interfaces.Miniconda,
                      'mrtrix3': interfaces.MRtrix3,
                      'neurodebian': interfaces.NeuroDebian,
                      'spm': interfaces.SPM,
                      }

from neurodocker.docker import DockerContainer, DockerImage
from neurodocker.dockerfile import Dockerfile
from neurodocker.parser import SpecsParser


def _get_version():
    """Return version string."""
    import os

    BASE_PATH = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(BASE_PATH, "VERSION"), 'r') as fp:
        return fp.read().strip()

__version__ = _get_version()
