"""Class to add FSL installation to Dockerfile."""
from __future__ import absolute_import, division, print_function

from .utils import indent
from ..utils import logger


INSTALL_FSL = {
    "5_0_8": {
        "xenial": {
            "method": "neurodebian",
            "deps": ["bzip2", "ca-certificates", "curl"],
        },
    },
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

    def _add_version_5_0_8(self):
        """Return Dockerfile instructions to install FSL 5.0.8, and add list
        of dependencies to `self.dependencies`."""
        pass
