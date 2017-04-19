"""Class to add Miniconda and create Conda environment."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
import logging
import os

from neurodocker.utils import check_url, indent, manage_pkgs

logger = logging.getLogger(__name__)


class Miniconda(object):
    """Add Dockerfile instructions to install Miniconda and requested packages.

    Parameters
    ----------
    python_version : str
        Version of Python to install. For example, '3.6.1'.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    conda_install : str or list or tuple
        Packages to install using `conda`. Follow the syntax for
        `conda install`. For example, the input ['numpy=1.12', 'scipy'] is
        interpreted as `conda install numpy=1.12 scipy`. The conda-forge channel
        is added by default.
    pip_install : str or list or tuple
        Packages to install using `pip`. Follow the syntax for `pip install`.
        For example, the input "https://github.com/nipy/nipype/" is interpreted
        as `pip install https://github.com/nipy/nipype/`.
    miniconda_verion : str
        Version of Miniconda to install. Defaults to 'latest'. This does not
        correspond to Python version.
    check_urls : bool
        If true, throw warning if a URL used by this class responds with a
        status code greater than 400.
    """
    def __init__(self, python_version, pkg_manager, conda_install=None,
                 pip_install=None, miniconda_verion='latest', check_urls=True):
        self.python_version = python_version
        self.pkg_manager = pkg_manager
        self.conda_install = conda_install
        self.pip_install = pip_install
        self.miniconda_verion = miniconda_verion
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        comment = ("#-------------------------------------------------\n"
                   "# Install Miniconda, and set up Python environment\n"
                   "#-------------------------------------------------")
        return "\n".join((comment, self.install_miniconda(),
                          self.install_pkgs()))

    def install_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""
        install_url = ("https://repo.continuum.io/miniconda/"
                       "Miniconda3-{}-Linux-x86_64.sh"
                       "".format(self.miniconda_verion))
        if self.check_urls:
            check_url(install_url)

        workdir_cmd = "WORKDIR /opt"
        miniconda_cmd = ("deps='bzip2 ca-certificates wget'\n"
                         "&& {install}\n"
                         "&& wget -qO miniconda.sh {url}\n"
                         "&& bash miniconda.sh -b -p /opt/miniconda\n"
                         "&& rm -f miniconda.sh\n"
                         "&& {remove}\n"
                         "&& {clean}"
                         "".format(url=install_url,
                            **manage_pkgs[self.pkg_manager]))
        miniconda_cmd = miniconda_cmd.format(pkgs="$deps")
        miniconda_cmd = indent("RUN", miniconda_cmd)
        env_cmd = "ENV PATH=/opt/miniconda/bin:$PATH"
        return "\n".join((workdir_cmd, miniconda_cmd, env_cmd))

    @staticmethod
    def _install_conda_pkgs(python_version, conda_install):
        base_cmd = "\n&& conda install -y -q python={}".format(python_version)
        if conda_install is not None:
            if isinstance(conda_install, (list, tuple)):
                conda_install = " ".join(conda_install)
            return " ".join((base_cmd, conda_install))
        else:
            return base_cmd

    @staticmethod
    def _install_pip_pkgs(pip_install):
        if pip_install is not None:
            if isinstance(pip_install, (list, tuple)):
                pip_install = " ".join(pip_install)
            return ("\n&& pip install -q --no-cache-dir {}"
                    "".format(pip_install))
        else:
            return ""

    def install_pkgs(self):
        cmds = [self._install_conda_pkgs(self.python_version, self.conda_install),
                self._install_pip_pkgs(self.pip_install)]
        pkgs_cmd = ("conda config --add channels conda-forge"
                    "{0}"
                    "{1}"
                    "\n&& conda clean -y --all"
                    "".format(*cmds))
        return indent("RUN", pkgs_cmd)
