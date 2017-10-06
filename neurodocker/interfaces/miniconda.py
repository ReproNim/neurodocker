"""Class to add Miniconda and create Conda environment."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

# Refer to the jupyter base-notebook Dockerfile for good practices:
# https://github.com/jupyter/docker-stacks/blob/master/base-notebook/Dockerfile

from __future__ import absolute_import, division, print_function
import logging
import posixpath

from neurodocker.utils import _indent_pkgs, check_url, indent, is_url

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
    yaml_file : path-like or url-like
        Conda environment specification file.
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
    miniconda_version : str
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

    def __init__(self, env_name, pkg_manager, yaml_file=None,
                 conda_install=None, pip_install=None, conda_opts=None,
                 pip_opts=None, add_to_path=False, miniconda_version='latest',
                 check_urls=True):
        self.env_name = env_name
        self.yaml_file = yaml_file
        self.pkg_manager = pkg_manager
        self.conda_install = conda_install
        self.pip_install = pip_install
        self.conda_opts = conda_opts
        self.pip_opts = pip_opts
        self.add_to_path = add_to_path
        self.miniconda_version = miniconda_version
        self.check_urls = check_urls

        self._check_args()
        self.cmd = self._create_cmd()

    def _check_args(self):
        if self.yaml_file and (self.conda_install is not None
                               or self.pip_install is not None):
            raise ValueError("Packages cannot be installed while creating an"
                             " environment from a yaml file.")

    def _create_cmd(self):
        cmds = []
        comment = ("#------------------"
                   "\n# Install Miniconda"
                   "\n#------------------")
        if not Miniconda.INSTALLED:
            cmds.append(comment)
            cmds.append(self.install_miniconda())
            cmds.append('')

        create = self.env_name not in Miniconda.created_envs
        _comment_base = "Create" if create else "Update"
        comment = ("#-------------------------"
                   "\n# {} conda environment"
                   "\n#-------------------------").format(_comment_base)
        cmds.append(comment)
        if self.yaml_file is not None:
            cmds.append(self.create_from_yaml())
        else:
            cmds.append(self.conda_and_pip_install(create=create))

        return "\n".join(cmds)

    def install_miniconda(self):
        """Return Dockerfile instructions to install Miniconda."""

        install_url = ("https://repo.continuum.io/miniconda/"
                       "Miniconda3-{}-Linux-x86_64.sh"
                       "".format(self.miniconda_version))
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

    def create_from_yaml(self):
        """Return Dockerfile instructions to create conda environment from
        a YAML file.
        """
        tmp_yml = "/tmp/environment.yml"
        cmd = ("conda env create -q --name {n} --file {tmp}"
               "\n&& rm -f {tmp}")

        if is_url(self.yaml_file):
            get_file = "curl -sSL {f} > {tmp}"
            cmd = get_file + "\n&& " + cmd
            if self.check_urls:
                check_url(self.yaml_file)
            cmd = indent("RUN", cmd)
        else:
            get_file = 'COPY ["{f}", "{tmp}"]'
            cmd = indent("RUN", cmd)
            cmd = "\n".join((get_file, cmd))

        cmd = cmd.format(n=self.env_name, f=self.yaml_file, tmp=tmp_yml)

        if self.add_to_path:
            bin_path = posixpath.join(Miniconda.INSTALL_PATH, 'envs',
                                      self.env_name, 'bin')
            env_cmd = "ENV PATH={}:$PATH".format(bin_path)
            return "\n".join((cmd, env_cmd))
        return cmd

    def conda_and_pip_install(self, create=True):
        """Return Dockerfile instructions to create conda environment with
        desired version of Python and desired conda and pip packages.
        """
        conda_cmd = "conda create" if create else "conda install"
        cmd = "{} -y -q --name {}".format(conda_cmd, self.env_name)

        if self.conda_opts:
            cmd = "{} {}".format(cmd, self.conda_opts)

        if self.conda_install:
            if isinstance(self.conda_install, str):
                self.conda_install = self.conda_install.split()
            pkgs = _indent_pkgs(len(cmd.split('\n')[-1]), self.conda_install)
            cmd += pkgs
            # cmd += "\n\t{}".format(self.conda_install)

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
        if isinstance(self.pip_install, str):
            self.pip_install = self.pip_install.split()

        cmd = ('/bin/bash -c "source activate {}'
               '\n  && pip install -q --no-cache-dir').format(self.env_name)

        if self.pip_opts:
            cmd = "{} {}".format(cmd, self.pip_opts)

        pkgs = _indent_pkgs(len(cmd.split('\n')[-1]), self.pip_install)

        return '{}{}"\n&& sync'.format(cmd, pkgs)

    @classmethod
    def clear_memory(cls):
        cls.INSTALLED = False
        cls.created_envs = []
