"""Class to add Miniconda and create Conda environment."""
from __future__ import absolute_import, division, print_function
import os

from .utils import indent
from ..utils import logger, save_yaml, check_url


class Miniconda(object):
    """Class to add Miniconda installation and Conda environment to Dockerfile.

    Parameters
    ----------
    conda_env : dict
        Dictionary of environment specifications.
        See https://github.com/conda/conda/tree/master/conda_env.
    filepath : str
        Path to save environment file. Must be saved within
        the scope of the Dockerfile.
    miniconda_version : str
        Version of Miniconda to use. Defaults to "latest".
    """
    def __init__(self, conda_env, filepath, miniconda_version="latest"):
        self.conda_env = conda_env
        self.filepath = os.path.join(filepath, "conda-env.yml")
        self.miniconda_version = miniconda_version
        self.dependencies = {
            'apt-get': ['bzip2', 'ca-certificates', 'curl'],
            'yum': ['bzip2', 'ca-certificates', 'curl'], }

        comment = "# Install Miniconda, and create Conda environment from file."
        self.cmd = "\n".join((comment, self._add_miniconda(),
                              self._add_conda_env()))

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

        # Add Miniconda to PATH.
        env_cmd = ("CONDAPATH=/usr/local/miniconda/bin\n"
                   "LANG=C.UTF-8\n"
                   "LC_ALL=C.UTF-8".format(miniconda_path))
        env_cmd = indent("ENV", env_cmd, line_suffix=" \\")

        return "\n".join((download_cmd, env_cmd))

    def _add_conda_env(self, env_name="new_env"):
        """Return Dockerfile instructions to create new Conda environment based
        on the specifications in `conda_env`.
        """
        # Save Conda environment YAML file and copy this file to /home
        # directory in Docker container. YAML file must be saved in scope of
        # Dockerfile.
        docker_filepath = "/home/{}".format(os.path.basename(self.filepath))
        base_name = os.path.basename(self.filepath)
        copy_cmd = "COPY {} {}".format(base_name, docker_filepath)

        # Set up a command to create and source new environment.
        # Is it necessary to update conda?
        create_env_cmd = ("$CONDAPATH/conda update -y conda\n"
                          "$CONDAPATH/conda env create -f {} -n {}\n"
                          # Delete the root conda environment. This frees up
                          # ~200 MB of space.
                          "cd $CONDAPATH/../ && rm -rf "
                          "conda-meta include share ssl\n"
                          "$CONDAPATH/conda clean -y -a"
                          "".format(docker_filepath, env_name, env_name))
        create_env_cmd = indent("RUN", create_env_cmd, " && \\")

        env_cmd = "PATH=/usr/local/miniconda/envs/{}/bin:$PATH".format(env_name)
        env_cmd = indent("ENV", env_cmd, line_suffix=' \\')

        return "\n".join((copy_cmd, create_env_cmd, env_cmd))

    def _save_conda_env(self):
        """Save Conda environment specs and YAML file. File must be saved
        in order to be copied into Docker container. Where should we save? In
        the Dockerfile class?"""
        save_yaml(self.conda_env, self.filepath)
