"""Add Dockerfile instructions to minimize container with ReproZip.

Project repository: https://github.com/ViDA-NYU/reprozip/

See https://github.com/freesurfer/freesurfer/issues/70 for an example of using
ReproZip to minimize Freesurfer's recon-all command.

To use the reprozip trace, Docker images must be built with
`--security-opt seccomp:unconfined` to allow ReproZip trace to work.

Docker's use of layers means that even if a smaller container is committed from
a larger image there will be no reduction in size (the previous layers are
preserved). Look into the `--squash` option in `docker build`. One idea is to
use the command `docker build --squash ...` when minifying images.

See https://github.com/moby/moby/issues/332 and
https://github.com/moby/moby/pull/22641.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import os
import posixpath

from neurodocker.utils import indent, manage_pkgs

# TODO: it seems that ReproZip can only be used when running a container, not
#       when building from a Dockerfile (at least on macOS).
#
# An option:
# 1. Build image as usual.
# 2. Run container.
# 3. Within running container, install dedicated miniconda with reprozip.
# 4. Within running container, run reprozip (with security-opt) on command(s),
#    and remove files not caught by the trace.
# 5. Export that container, and import it as a new, minified image.
#    https://stackoverflow.com/a/22714556/5666087


class Reprozip(object):
    """Add Dockerfile instructions to minimize a container based on a command
    or a list of commands.

    First, reprozip trace is run on a command or a list of commands, and then
    all files are deleted except those in the reprozip trace output.

    Parameters
    ----------
    cmds : str or list
        Command(s) to run to minimize the image.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    """
    CONDA_ROOT = "/opt/.reprozip-miniconda"

    def __init__(self, cmds, pkg_manager, trace_dir="/.reprozip-trace"):
        # TODO: add option for various methods of minifying:
        # 1. remove all files in container except those found by reprozip.
        # 2. save reprozip pack file and create new docker image with
        #    reprounzip-docker.

        self.cmds = cmds
        self.pkg_manager = pkg_manager
        self.trace_dir = trace_dir

        if isinstance(self.cmds, str):
            self.cmds = [self.cmds]

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install and run ReproZip."""
        comment = ("#-----------------------------\n"
                   "# Install and run ReproZip\n"
                   "# (build with --squash option)\n"
                   "#-----------------------------\n")
        cmds = (self.install_miniconda(), self.install_reprozip(),
                self.trace(), self.remove_untraced_files())
        cmds = indent("RUN", ''.join(cmds))
        return comment + cmds

    def install_miniconda(self):
        """Install Miniconda solely for reprozip. Do not add this installation
        to PATH.
        """
        url = ("https://repo.continuum.io/miniconda/"
               "Miniconda3-latest-Linux-x86_64.sh")
        return ("curl -ssL -o miniconda.sh {}"
                "\n&& bash miniconda.sh -b -p {}"
                "\n&& rm -f miniconda.sh".format(url, Reprozip.CONDA_ROOT))

    def install_reprozip(self):
        """Conda install reprozip from the vida-nyu channel."""
        conda = posixpath.join(Reprozip.CONDA_ROOT, 'bin', 'conda')
        return ("\n&& {conda} install -y -q python=3.5 pyyaml"
                "\n&& {conda} install -y -q -c vida-nyu reprozip"
                "".format(conda=conda))

    def trace(self):
        """Run reprozip trace on the specified commands."""
        reprozip = posixpath.join(Reprozip.CONDA_ROOT, 'bin', 'reprozip')
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
        """Return command to remove files that were not caught by reprozip
        trace.
        """
        kwargs = {'python': posixpath.join(Reprozip.CONDA_ROOT, 'bin',
                                           'python'),
                  'script_url': 'https://dl.dropbox.com/s/tuar1ykz7wly1yy/_reprozip_rm_files.py',
                  'save_path': '/tmp/rm_untraced_files.py',
                  'config_path': os.path.join(self.trace_dir, 'config.yml'),
                  'miniconda': Reprozip.CONDA_ROOT,}

        return ("\n&& curl -sSL -o {save_path} {script_url}"
                "\n&& {python} {save_path} --rm {config_path} {miniconda}"
                "\n&& rm -rf {miniconda}".format(**kwargs))
