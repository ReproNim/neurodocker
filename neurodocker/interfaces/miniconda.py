"""Class to add Miniconda and create Conda environment."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function
import logging
import posixpath

from neurodocker.utils import check_url, indent

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
        If true, raise error if a URL used by this class responds with an error
        code.
    """

    def __init__(self, python_version, pkg_manager, conda_install=None,
                 pip_install=None, miniconda_verion='latest', check_urls=True):
        self.python_version = python_version
        self.pkg_manager = pkg_manager
        self.conda_install = conda_install
        self.pip_install = pip_install
        self.miniconda_verion = miniconda_verion
        self.check_urls = check_urls

        self._install_path = "/opt/miniconda"
        self._env_name = "default"
        self._env_path = posixpath.join(self._install_path, "envs",
                                             self._env_name)
        self.cmd = self._create_cmd()

    def _create_cmd(self):
        comment = ("#-------------------------------------------------\n"
                   "# Install Miniconda, and set up Python environment\n"
                   "#-------------------------------------------------")

        bin_path = posixpath.join(self._env_path, "bin")
        env_cmd = "ENV PATH={}:$PATH".format(bin_path)

        cmd_kwargs = {'install_miniconda': self._install_miniconda(),
                      'conda': self._create_conda_env(),
                      'pip': self._install_pip_pkgs(),
                      'miniconda_dir': self._install_path,}

        cmd = ("{install_miniconda}"
               "\n&& {miniconda_dir}/bin/conda config --add channels conda-forge"
               "{conda}"
               "{pip}"
               "\n&& rm -rf {miniconda_dir}/[!envs]*"
               "".format(**cmd_kwargs))
        cmd = indent("RUN", cmd)

        return "\n".join((comment, env_cmd, cmd))

    def _install_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""
        install_url = ("https://repo.continuum.io/miniconda/"
                       "Miniconda3-{}-Linux-x86_64.sh"
                       "".format(self.miniconda_verion))
        if self.check_urls:
            check_url(install_url)

        miniconda_cmd = ('echo "Downloading Miniconda installer ..."'
                         "\n&& curl -sSL -o miniconda.sh {}"
                         "\n&& bash miniconda.sh -b -p {}"
                         "\n&& rm -f miniconda.sh"
                         "".format(install_url, self._install_path))
        return miniconda_cmd

    def _create_conda_env(self):
        """Return command to create conda environment with desired version
        of Python and desired conda packages.
        """
        orig_conda = posixpath.join(self._install_path, "bin", "conda")

        cmd = ("\n&& {} create -y -q -n default python={}"
               "".format(orig_conda, self.python_version))

        if self.conda_install is not None and self.conda_install:
            if isinstance(self.conda_install, (list, tuple)):
                self.conda_install = " ".join(self.conda_install)
            cmd = "\n\t".join((cmd, self.conda_install))

        cmd += "\n&& conda clean -y --all"
        return cmd

    def _install_pip_pkgs(self):
        """Return command to install desired pip packages."""

        if self.pip_install is not None and self.pip_install:
            if isinstance(self.pip_install, (list, tuple)):
                self.pip_install = " ".join(self.pip_install)

            cmd = ("\n&& pip install -U -q --no-cache-dir pip"
                   "\n&& pip install -q --no-cache-dir\n\t{}"
                   "".format(self.pip_install))
            return cmd
        return ""
