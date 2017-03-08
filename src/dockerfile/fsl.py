"""Class to add FSL installation to Dockerfile."""
from __future__ import absolute_import, division, print_function

from .utils import indent
from ..utils import logger


INSTALL_FSL = {
    "xenial": {
        "deps": ["bzip2", "ca-certificates", "curl"],
        "method": "neurodebian"
    }
}


class FSL(object):
    """Class to add FSL installation to Dockerfile.

    Parameters
    ----------
    os : str
        Operating system. Should this correspond to a docker image:tag?
    version: str
        Version of FSL.
    """
    def __init__(self, os, version):
        self.os = os
        self.version = version
