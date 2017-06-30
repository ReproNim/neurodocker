"""Functions and classes to generate Dockerfiles."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from neurodocker import SUPPORTED_SOFTWARE
from neurodocker.interfaces import Miniconda
from neurodocker.utils import indent, manage_pkgs


class Dockerfile(object):
    """Class to create Dockerfile.

    Parameters
    ----------
    specs : dict
        Dictionary of specifications. Recommended to pass the dictionary
        through neurodocker.SpecsParser first.
    pkg_manager : {'apt', 'yum'}
        Linux package manager. If None, uses the value of `specs['pkg_manager']`.
    check_urls : bool
        If true, throw warning if a URL used by this class responds with a
        status code greater than 400.
    """

    def __init__(self, specs, pkg_manager=None, check_urls=True):
        self.specs = specs

        try:
            self.pkg_manager = self.specs['pkg_manager']
        except KeyError:
            self.pkg_manager = pkg_manager

        try:
            self.check_urls = self.specs['check_urls']
        except KeyError:
            self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def __repr__(self):
        return "{self.__class__.__name__}({self.cmd})".format(self=self)

    def __str__(self):
        return self.cmd

    def _create_cmd(self):
        cmds = [self.add_base()]

        if 'debian' in self.specs['base'] or 'ubuntu' in self.specs['base']:
            cmds.append("ARG DEBIAN_FRONTEND=noninteractive")

        cmds.append(self.add_common_dependencies())

        # Install Miniconda before other software.
        if "miniconda" in self.specs.keys():
            cmds.append(self.add_miniconda())

        software_cmds = self.add_software()
        if software_cmds:
            cmds.append(software_cmds)

        # Add arbitrary Dockerfile instructions.
        try:
            comment = ("\n#--------------------------"
                       "\n# User-defined instructions"
                       "\n#--------------------------")
            cmds.append(comment)
            cmds.extend(self.specs['instruction'])
        except KeyError:
            pass

        return "\n\n".join(cmds) + "\n"

    def add_base(self):
        """Add Dockerfile FROM instruction."""
        return "FROM {}".format(self.specs['base'])

    def add_common_dependencies(self):
        """Add Dockerfile instructions to download dependencies common to many
        software packages.
        """
        deps = "bzip2 ca-certificates curl unzip"
        comment = ("#----------------------------\n"
                   "# Install common dependencies\n"
                   "#----------------------------")
        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        cmd = cmd.format(pkgs=deps)
        cmd = indent("RUN", cmd)

        return "\n".join((comment, cmd))

    def add_miniconda(self):
        """Add Dockerfile instructions to install Miniconda."""
        kwargs = self.specs['miniconda']
        obj = Miniconda(pkg_manager=self.pkg_manager,
                        check_urls=self.check_urls, **kwargs)

        return obj.cmd

    def add_software(self):
        """Add Dockerfile instructions to install neuroimaging software."""
        cmds = []
        for pkg, kwargs in self.specs.items():
            if pkg == 'miniconda':
                continue
            if pkg in SUPPORTED_SOFTWARE.keys():
                obj = SUPPORTED_SOFTWARE[pkg](pkg_manager=self.pkg_manager,
                                              check_urls=self.check_urls,
                                              **kwargs)
                cmds.append(obj.cmd)

        return "\n\n".join(cmds)

    def save(self, filepath="Dockerfile", **kwargs):
        """Save Dockerfile to `filepath`. `kwargs` are for `open()`."""
        with open(filepath, mode='w', **kwargs) as fp:
            fp.write(self.cmd)
