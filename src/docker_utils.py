"""Classes to generate Dockerfile, build Docker image, and run script within
Docker container.
"""
from __future__ import absolute_import, division, print_function
import os

import docker

# Begin talking with Docker daemon.
client = docker.from_env()


def indent(docker_cmd, text, line_suffix=''):
    """Add Docker command and indent text."""
    amount = len(docker_cmd) + 1
    indent = ' ' * amount
    split_lines = text.splitlines()

    if len(split_lines) == 1:
        return "{} {}".format(docker_cmd, text)

    out = ''
    for i, line in enumerate(split_lines):
        if i == 0:  # First line.
            out += "{} {}{}".format(docker_cmd, line, line_suffix)
        elif i == len(split_lines) - 1:  # Last line.
            out += "\n{}{}".format(indent, line)
        else:
            out += "\n{}{}{}".format(indent, line, line_suffix)
    return out



class Dockerfile(object):
    """Object to create Dockerfile and build Docker image.

    Parameters
    ----------
    specs : dict
        Software specifications for the Dockerfile. Keys include 'base',
        'py_version', and 'py_pkgs' so far.

    TODO
    ----
    If dependencies need to be installed via apt-get, yum, etc., combine all of
    those dependencies so they can be installed using one RUN command.
    """
    def __init__(self, specs):
        self.specs = specs
        # self.path = op.abspath(path)
        # self.img_name = img_name
        self._cmds = []  # List of Dockerfile commands.

        if self.specs['base'] is None:
            raise Exception("key `base` is required")

    def add_command(self, cmd):
        """Generic function to add any Dockerfile command.

        Parameters
        ----------
        cmd : str
            Dockerfile command to be added.
        """
        self._cmds.append(cmd)

    def add_base(self):
        """Return Dockerfile command to use the baseimage `base`.

        Parameters
        ----------
        base : str
            The base image and its version (e.g., Ubuntu:16.04). Does the base
            image have to be hosted on Dockerhub?
        """
        cmd = "FROM {}".format(self.specs['base'])
        self._cmds.append(cmd)

    def add_afni(self):
        """Add Dockerfile to install ANTs software.

        NOTE: This has to be fixed. Should we build from source? Are the
        binaries for previous versions stored somewhere online?
        """
        comments = ["# Install AFNI dependencies.", "# Install AFNI."]
        cmd = ("apt-get -y -qq install libxp6 libglu1-mesa gsl-bin "
               "libjpeg62-dev libxft-dev")
        cmd = indent("RUN", cmd, ' \\')

        base_url = "https://afni.nimh.nih.gov/pub/dist/tgz/"
        install_file = "linux_openmp_64.tgz"
        install_url = base_url + install_file
        install_cmd = ("curl -L {} | tar zxC /usr/local\n"
                       "mv /usr/local/linux_openmp_64 /usr/local/afni"
                       "".format(install_url, install_file))
        install_cmd = indent("RUN", install_cmd, " && \\")

        env_cmd = "ENV PATH $PATH:/usr/local/afni"

        cmd = "\n".join((comments[0], cmd, comments[1], install_cmd, env_cmd))
        self._cmds.append(cmd)

    def add_miniconda(self, miniconda_version='latest'):
        """Return Dockerfile command to install Miniconda.

        Parameters
        ----------
        miniconda_version : str
            Miniconda version. Defaults to 'latest'.
        """
        py_version = self.specs['py_version']

        comments = ["# Install miniconda.",
                    "# Define environment variables.",
                    "# Install Python {}.".format(py_version)]

        base_url = "https://repo.continuum.io/miniconda/"
        install_file = ("Miniconda{}-{}-Linux-x86_64.sh"
                        "".format(py_version[0], miniconda_version))
        install_url = base_url + install_file

        # curl and bzip2 have to be installed.
        install_cmd = ("curl -sSLO {url}\n"
                       "/bin/bash {file} -b -p /usr/local/miniconda\n"
                       "rm {file}".format(url=install_url, file=install_file))
        # Add Docker RUN command and indent lines.
        install_cmd = indent("RUN", install_cmd, line_suffix=" && \\")

        # Clean this up.
        env_cmd = ("PATH=/usr/local/miniconda/bin:$PATH\n"
                   "PYTHONNOUSERSITE=1\n"
                   "LANG=C.UTF-8\n"
                   "LC_ALL=C.UTF-8"
                   "".format(py_version[:3]))
        # Add Docker command ENV and indent lines.
        env_cmd = indent("ENV", env_cmd, line_suffix=" \\")

        # Install the requested Python version. Is there a way to install this
        # version of Python when installing Miniconda? In the latest
        # installation shell script, it looks like Miniconda defaults to
        # Python 3.6.
        conda_python_cmd = ("RUN conda install python={}".format(py_version))

        cmd = "\n".join((comments[0], install_cmd, comments[1], env_cmd,
                        comments[2], conda_python_cmd))
        self._cmds.append(cmd)

    def add_python_pkgs(self):
        """Return Dockerfile command to install Python packages.

        TODO
        ----
        For the packages that cannot be installed with conda, try pip. If that
        fails, what can be done?
        """
        if not self.specs['py_version']:
            raise Exception("Python version must be specified in order to add "
                            "Python packages")

        comment = "# Install Python packages."
        install_list = []
        for item in self.specs['py_pkgs']:
            if isinstance(item, tuple):  # e.g., ('numpy', '1.10')
                install_str = "{}=={}".format(item[0], item[1])
                install_list.append(install_str)
            elif isinstance(item, str):  # e.g., 'numpy'
                install_list.append(item)

        add_channel_cmd = "conda config --add channels conda-forge"
        install_cmd = "conda install -y " + ' '.join(install_list)

        # Combine the conda commands.
        cmd = "\n".join((add_channel_cmd, install_cmd))
        cmd = indent("RUN", cmd, line_suffix=" && \\")

        cmd = "\n".join((comment, cmd))  # Add comment.
        self._cmds.append(cmd)

    def _create(self):
        """Return Dockerfile as string.

        TODO
        ----
        Try to combine all of the packages to get via apt-get or yum etc. into
        one RUN command.
        """
        reqs_cmd = ("apt-get update && apt-get install -yq\n"
                    "--no-install-recommends\n"
                    "bzip2\n"
                    "ca-certificates\n"
                    "curl\n"
                    "wget\n"
                    "xvfb")
        if self.specs['base']:
            self.add_base()
        self.add_command("RUN", reqs_cmd, ' \\')
        # if self.specs['afni']:
        #     self.add_afni()
        if self.specs['py_version']:
            self.add_miniconda()
        if self.specs['py_pkgs']:
            self.add_python_pkgs()
        return '\n\n'.join(self._cmds)

    def save(self, path=None):
        """Save Dockerfile."""
        obj = self._create()
        if path is None:
            path = "."
        file_path = op.join(self.path, "Dockerfile")
        with open(file_path, 'w') as stream:
            stream.write(obj)

    def build(self, path=None, tag=None):
        """Save Dockerfile and build Docker image from saved Dockerfile.

        Returns
        -------
        image : docker.Image

        TODO
        ----
        Should we not save the Dockerfile? Maybe we can build using the string,
        and we can save separately.
        """
        if path is None:
            path = "."
        self.save(path)
        print("Building Docker image")
        # How do we display the console output while building?
        return client.images.build(path=path, tag=tag)



class DockerCommand(object):
    """ """
    def __init__(self, image, cmd=None, volumes=[]):
        self.image = image
        self.cmd = cmd
        self.volumes = volumes
        if self.volumes:
            self.volumes = self._fmt_vols()

    def _fmt_vols(self):
        volumes = {}
        for vol in self.volumes:
            local, mnt = vol.split(':')
            if os.path.exists(local):
                volumes[os.path.abspath(local)] = {"bind": mnt}
        return volumes

    def run(self):
        """Run the command within the Docker image."""
        pass
        #
