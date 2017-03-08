"""Class to generate Dockerfile."""
from __future__ import absolute_import, division, print_function

from .utils import indent
from ..utils import logger



class Dockerfile(object):
    """Class to generate Dockerfile.

    Parameters
    ----------
    specs : dict
        Software specifications for the Dockerfile.

    TODO
    ----
    - Combine all dependencies into one RUN instruction.
    """
    def __init__(self, specs):
        self.specs = specs
        self._cmds = []

    def add_command(self, cmd):
        """Add command `cmd`."""
        self._cmds.append(cmd)

    def _add_base(self):
        """Add FROM instruction using specs['base']."""
        cmd = "FROM {}".format(self.specs['base'])
        self.add_command(cmd)
