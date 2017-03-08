"""Class to add Miniconda and/or Python packages to Dockerfile."""
from __future__ import absolute_import, division, print_function
import os

from .utils import check_url, indent
from ..utils import logger, save_yaml



class Miniconda(object):
    """Class to add Miniconda installation and Python packages to Dockerfile.

    Parameters
    ----------
    conda_env : dict
        Dictionary of environment specifications.
        See https://github.com/conda/conda/tree/master/conda_env.
    miniconda_version : str
        Version of Miniconda to use. Defaults to "latest".
    """
    def __init__(self, conda_env, miniconda_version="latest"):
        self.conda_env = conda_env
        self.miniconda_version = miniconda_version

        self.cmd = self._add_miniconda()

    def _add_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""
        base_url = "https://repo.continuum.io/miniconda/"
        install_file = ("Miniconda3-{}-Linux-x86_64.sh"
                        "".format(self.miniconda_version))
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
        create_env_cmd = self._create_env()

        return "\n".join((download_cmd, env_cmd, create_env_cmd))

    def _create_env(self):
        """Create new environment based on the specifications in `conda_env`.
        """
        # try:
        #     env_name = self.conda_env['name']
        # except KeyError:
        #     raise KeyError("`name` must be specified in `conda-env`.")
        # Save YAML file.
        filepath = "environment.yml"
        docker_filepath = "/home/{}".format(filepath)
        save_yaml(self.conda_env, filepath)

        # COPY that file into the Docker image.
        copy_cmd = "COPY {} {}".format(filepath, docker_filepath)

        # Set up a command to create (and source) new environment.
        create_env_cmd = ("conda env create -f {} -n new_env\n"
                          "source activate new_env\n"
                          "".format(docker_filepath))
        create_env_cmd = indent("RUN", create_env_cmd, " && \\")

        return "\n".join((copy_cmd, create_env_cmd))
