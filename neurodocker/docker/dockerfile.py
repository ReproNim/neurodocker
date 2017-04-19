"""Class to generate Dockerfile."""
from __future__ import absolute_import, division, print_function
import os

from neurodocker.docker.miniconda import Miniconda
from neurodocker.utils import logger, SUPPORTED_NI_SOFTWARE


class Dockerfile(object):
    """Class to create Dockerfile.

    Parameters
    ----------
    specs : dict
        Dictionary with keys 'base', etc.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    check_urls : bool
        If true, throw warning if a URL used by this class responds with a
        status code greater than 400.
    """

    def __init__(self, specs, pkg_manager, check_urls=True):
        self.specs = specs
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls
        self._cmds = []

        self.add_base()
        if "conda_env" in self.specs.keys():
            self.add_miniconda()
        if "software" in self.specs.keys():
            self.add_ni_software()

        self.cmd = "\n\n".join(self._cmds)

    def __repr__(self):
        return "{self.__class__.__name__}({self.cmd})".format(self=self)

    def __str__(self):
        return self.cmd

    def add_instruction(self, instruction):
        self._cmds.append(instruction)

    def add_base(self):
        """Add Dockerfile FROM instruction."""
        cmd = "FROM {}".format(self.specs['base'])
        self.add_instruction(cmd)

    def add_miniconda(self):
        """Add Dockerfile instructions to install Miniconda."""
        kwargs = self.specs['conda_env']
        obj = Miniconda(pkg_manager=self.pkg_manager,
                        check_urls=self.check_urls, **kwargs)
        self.add_instruction(obj.cmd)


    def add_ni_software(self):
        """Add Dockerfile instructions to install neuroimaging software."""
        software = self.specs['software']
        for pkg, kwargs in software.items():
            obj = SUPPORTED_NI_SOFTWARE[pkg](pkg_manager=self.pkg_manager,
                                             check_urls=self.check_urls,
                                             **kwargs)
            self.add_instruction(obj.cmd)

    def save(self, filepath="Dockerfile", **kwargs):
        """Save `self.cmd` to `filepath`. `kwargs` are for `open()`."""
        if not self.cmd:
            raise Exception("Instructions are empty.")
        with open(filepath, mode='w', **kwargs) as fp:
            fp.write(self.cmd)
            fp.write('\n')
