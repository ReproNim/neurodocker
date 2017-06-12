"""Add Dockerfile instructions to minimize container with ReproZip.

Project repository: https://github.com/ViDA-NYU/reprozip/

See https://github.com/freesurfer/freesurfer/issues/70 for an example of using
ReproZip to minimize Freesurfer's recon-all command.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import posixpath

from neurodocker.utils import indent, manage_pkgs


class Reprozip(object):
    """Add Dockerfile instructions to minimize a container based on a command
    or a list of commands.

    First, reprozip trace is run on a command or a list of commands, and then
    all files are deleted except those in the reprozip trace output.

    Parameters
    ----------
    cmds : str or list
        Command(s) to run to minimize the image. Double-quotes within commands
        will be escaped automatically.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    """
    def __init__(self, cmds, pkg_manager, trace_dir="/reprozip-trace"):
        self.cmds = cmds
        self.pkg_manager = pkg_manager
        self.trace_dir = trace_dir

        if isinstance(self.cmds, str):
            self.cmds = [self.cmds]

        self._conda_root = "/opt/miniconda-reprozip"

    def _create_cmd(self):
        """Return full command to install and run ReproZip."""
        comment = ("#-----------------\n"
                   "# Install ReproZip\n"
                   "#-----------------\n")
        cmds = (self._install_miniconda(), self._install_reprozip(),
                self.trace())
        cmds = indent("RUN", ''.join(cmds))
        return comment + cmds

    def _install_miniconda(self):
        """Install Miniconda solely for reprozip. Do not add this installation
        to PATH.
        """
        url = ("https://repo.continuum.io/miniconda/"
               "Miniconda3-latest-Linux-x86_64.sh")
        return ("curl -ssL -o miniconda.sh {}"
                "\n&& bash miniconda.sh -b -p {}"
                "\n&& rm -f miniconda.sh".format(url, self._conda_root))

    def _install_reprozip(self):
        """Conda install reprozip from the vida-nyu channel."""
        conda = posixpath.join(self._conda_root, 'bin', 'conda')
        return ("\n&& {conda} install -y -q python=3.5 pyyaml"
                "\n&& {conda} install -y -q -c vida-nyu reprozip"
                "".format(conda=conda))

    def trace(self):
        """Run reprozip trace on the specified commands."""
        reprozip = posixpath.join(self._conda_root, 'bin', 'reprozip')
        trace_cmds = []
        base = ('\n&& {reprozip} trace -d {trace_dir} --dont-identify-packages'
                ' {continue_}\n\t{cmd}')

        for i, cmd in enumerate(self.cmds):
            if not cmd:
                raise ValueError("Command to trace is empty.")
            continue_ = "--continue " if i else ""
            trace_cmds.append(base.format(cmd=cmd, reprozip=reprozip,
                                          trace_dir=self.trace_dir,
                                          continue_=continue_))

        return "".join(trace_cmds)

    def remove_untraced_files(self):
        # QUESTION: how do we deal with directories in config.yml?
        pass
