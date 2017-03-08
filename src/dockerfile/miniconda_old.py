"""Class to add Miniconda and/or Python packages to Dockerfile."""
from __future__ import absolute_import, division, print_function

from .utils import check_url, indent
from ..utils import logger



class Miniconda(object):
    """Class to add Miniconda installation and Python packages to Dockerfile.

    Parameters
    ----------
    python_version : str
        Version of Python to install (e.g., "3.5.1").
    miniconda_version : str
        Version of Miniconda to use. Defaults to "latest".
    python_pkgs : list
        List of str or tuples. String is package name, and tuple is
        ("pkg", "version").

    Notes
    -----
    Dockerfile: https://hub.docker.com/r/continuumio/miniconda/~/dockerfile/
    conda-env: https://github.com/conda/conda-env
    """
    def __init__(self, python_version, miniconda_version="latest",
                 python_pkgs=None):
        self.python_version = python_version
        self.miniconda_version = miniconda_version
        self.python_pkgs = python_pkgs

        if self.python_pkgs is None:
        miniconda_cmd = self._add_miniconda()
        python_pkgs_cmd = self.add_python_pkgs()

    def _add_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""
        base_url = "https://repo.continuum.io/miniconda/"
        install_file = ("Miniconda{}-{}-Linux-x86_64.sh"
                        "".format(self.python_version, self.miniconda_version))
        install_url = base_url + install_file

        # Warn if URL is not reachable.
        check_url(install_url)

        miniconda_path = "/usr/local/miniconda"
        # Download and install miniconda.
        download_cmd = ("curl -sSLO {url}\n"
                        "/bin/bash {file} -b -p {path} \n"
                        "rm {file}".format(url=install_url, file=install_file,
                                           path=miniconda_path))
        download_cmd = indent("RUN", download_cmd, line_suffix=" && \\")

        # Add miniconda to PATH.
        env_cmd = ("PATH {}/bin:$PATH\n"
                   "LANG C.UTF-8\n"
                   "LC_ALL C.UTF-8".format(miniconda_path))
        env_cmd = indent("ENV", env_cmd, line_suffix=" \\")

        # Install the requested version of Python.
        conda_cmd = "RUN conda install -y python={}".format(self.python_version)

        return "\n".join((download_cmd, env_cmd, conda_cmd))

    def add_python_pkgs(self):
        """Return Dockerfile instructions to install Python packages. Only
        supports conda install for now.

        TODO
        ----
        If the package is not on conda, install it with pip. Installations from
        GitHub cannot use conda.
        """
        to_install = []
        for item in self.python_pkgs:
            if isinstance(item, tuple):
                # Example: "numpy==1.12"
                one_pkg = "==".join(item[0], item[1])  # or *item
                to_install.append(one_pkg)
            elif isinstance(item, str):
                # Example: "numpy"
                to_install.append(item)
        to_install = "\n".join(to_install)
        cmd = ("conda config --add channels conda-forge && conda install -y\n{}"
               "".format(to_install))
        return indent("RUN", cmd, " \\")
