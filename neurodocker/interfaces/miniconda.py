"""Class to add Miniconda and create Conda environment."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

# Refer to the jupyter base-notebook Dockerfile for good practices:
# https://github.com/jupyter/docker-stacks/blob/master/base-notebook/Dockerfile

from __future__ import absolute_import, division, print_function
import logging
import posixpath

from neurodocker.utils import check_url, indent

logger = logging.getLogger(__name__)


class Miniconda(object):
    """Add Dockerfile instructions to install Miniconda and create a new
    environment with packages installed with conda and pip.

    Parameters
    ----------
    env_name : str
        Name to give this environment.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    conda_install : str or list or tuple
        Packages to install using `conda`, including Python. Follow the syntax
        for `conda install`. For example, the input ['numpy=1.12', 'scipy'] is
        interpreted as `conda install numpy=1.12 scipy`. The conda-forge
        channel is added by default.
    pip_install : str or list or tuple
        Packages to install using `pip`. Follow the syntax for `pip install`.
        For example, the input "https://github.com/nipy/nipype/" is interpreted
        as `pip install https://github.com/nipy/nipype/`.
    conda_opts : str
        Command-line options to pass to `conda create`. Eg. "-c vida-nyu"
    pip_opts : str
        Command-line options to pass to `pip install`.
    add_to_path : bool
        If true, prepend the new environment to $PATH. False by default.
    miniconda_verion : str
        Version of Miniconda to install. Defaults to 'latest'. This does not
        correspond to Python version.
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.

    Notes
    -----
    Miniconda is installed once by the root user in /opt/conda. Separate conda
    environments can be created by non-root users.
    """

    created_envs = []
    INSTALLED = False
    INSTALL_PATH = "/opt/conda"

    def __init__(self, env_name, pkg_manager, conda_install=None,
                 pip_install=None, conda_opts=None, pip_opts=None,
                 add_to_path=False, miniconda_verion='latest', check_urls=True):
        self.env_name = env_name
        self.pkg_manager = pkg_manager
        self.conda_install = conda_install
        self.pip_install = pip_install
        self.conda_opts = conda_opts
        self.pip_opts = pip_opts
        self.add_to_path = add_to_path
        self.miniconda_verion = miniconda_verion
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        cmds = []
        comment = ("#------------------"
                   "\n# Install Miniconda"
                   "\n#------------------")
        if not Miniconda.INSTALLED:
            cmds.append(comment)
            cmds.append(self.install_miniconda())
            cmds.append('')

        create = not (self.env_name in Miniconda.created_envs)
        _comment_base = "Create" if create else "Update"
        comment = ("#-------------------------"
                   "\n# {} conda environment"
                   "\n#-------------------------").format(_comment_base)
        cmds.append(comment)
        cmds.append(self.conda_and_pip_install(create=create))

        return "\n".join(cmds)

    def install_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""

        install_url = ("https://repo.continuum.io/miniconda/"
                       "Miniconda3-{}-Linux-x86_64.sh"
                       "".format(self.miniconda_verion))
        if self.check_urls:
            check_url(install_url)

        env_cmd = ("CONDA_DIR={0}"
                   "\nPATH={0}/bin:$PATH".format(Miniconda.INSTALL_PATH))
        env_cmd = indent("ENV", env_cmd)

        cmd = ('echo "Downloading Miniconda installer ..."'
               "\n&& miniconda_installer=/tmp/miniconda.sh"
               "\n&& curl -sSL -o $miniconda_installer {url}"
               "\n&& /bin/bash $miniconda_installer -b -p $CONDA_DIR"
               "\n&& rm -f $miniconda_installer"
               "\n&& conda config --system --prepend channels conda-forge"
               "\n&& conda config --system --set auto_update_conda false"
               "\n&& conda config --system --set show_channel_urls true"
               "\n&& conda update -y -q --all && sync"
               "\n&& conda clean -tipsy && sync"
               "".format(Miniconda.INSTALL_PATH, url=install_url))
        cmd = indent("RUN", cmd)

        Miniconda.INSTALLED = True

        return "\n".join((env_cmd, cmd))

    def conda_and_pip_install(self, create=True):
        """Return Dockerfile instructions to create conda environment with
        desired version of Python and desired conda and pip packages.
        """
        conda_cmd = "conda create" if create else "conda install"
        cmd = "{} -y -q --name {}".format(conda_cmd, self.env_name)

        if self.conda_opts:
            cmd = "{} {}".format(cmd, self.conda_opts)

        if self.conda_install:
            if isinstance(self.conda_install, (list, tuple)):
                self.conda_install = " ".join(self.conda_install)
            cmd += "\n\t{}".format(self.conda_install)

        cmd += "\n&& sync && conda clean -tipsy && sync"

        if not self.conda_install and not create:
            cmd = ""
        if self.pip_install:
            if self.conda_install or create:
                cmd += "\n&& "
            cmd += self._pip_install()

        cmd = indent("RUN", cmd)

        self.created_envs.append(self.env_name)

        if self.add_to_path:
            bin_path = posixpath.join(Miniconda.INSTALL_PATH, 'envs',
                                      self.env_name, 'bin')
            env_cmd = "ENV PATH={}:$PATH".format(bin_path)
            return "\n".join((cmd, env_cmd))
        return cmd

    def _pip_install(self):
        """Return Dockerfile instruction to install desired pip packages."""
        if isinstance(self.pip_install, (list, tuple)):
            self.pip_install = " ".join(self.pip_install)

        cmd = ('/bin/bash -c "source activate {}'
               '\n\t&& pip install -q --no-cache-dir').format(self.env_name)

        if self.pip_opts:
            cmd = "{} {}".format(cmd, self.pip_opts)

        return '{}\n\t{}"\n&& sync'.format(cmd, self.pip_install)

    @classmethod
    def clear_memory(cls):
        cls.INSTALLED = False
        cls.created_envs = []
