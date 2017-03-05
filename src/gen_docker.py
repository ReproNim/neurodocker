from __future__ import absolute_import, print_function
import argparse
from distutils.version import LooseVersion
import os.path as op

import docker

LATEST_PYTHON = "3.6.0"

# Begin talking with Docker daemon.
client = docker.from_env()


def get_docker_args():

    def pypacks(arg):
        """
        Python package argparse type-checker
        If valid arg, returns either as string (if no version is specified)
        or a 2-item tuple
        """
        if ':' not in arg:  # assume latest
            return arg
        try:
            package, version = arg.split(':')
            return package, version
        except:
            raise argparse.ArgumentTypeError(
                "Not a valid format. Packages can be specified by either "
                "{PACKAGE_NAME} or {PACKAGE_NAME,VERSION}")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-base', required=True,
                        help="The base image to build the docker file from.")
    parser.add_argument('-py', dest='py_version',
                        help="If used, install specific version of Python")
    parser.add_argument('-pp', dest='py_pkgs', type=pypacks, nargs="+",
                        help="Can specify {PACKAGE:VERSION} or just {PACKAGE}")
    args = parser.parse_args()
    if args.py_version:
        if LooseVersion(args.py_version) > LooseVersion(LATEST_PYTHON):
            raise Exception("Version of Python is not available yet!")
    return vars(args)


def indent(docker_cmd, text, line_suffix=''):
    """Add Docker command and indent."""
    amount = len(docker_cmd) + 1
    indent = ' ' * amount
    split_lines = text.splitlines()

    if len(split_lines) == 1:
        return "{} {}".format(docker_cmd, text)

    out = ''
    for i, line in enumerate(split_lines):
        if i == 0:
            out += "{} {}{}".format(docker_cmd, line, line_suffix)
        elif i == len(split_lines) - 1:
            out += "\n{}{}".format(indent, line)
        else:
            out += "\n{}{}{}".format(indent, line, line_suffix)
    return out



class Dockerfile(object):
    """Dockerfile object.

    Parameters
    ----------
    specs : dict
        Software specifications for the Dockerfile. Keys include 'base',
        'py_version', and 'py_pkgs' (so far)
    """
    def __init__(self, specs, img_name, path='.'):
        self.specs = specs
        self.path = op.abspath(path)
        self.img_name = img_name
        self._cmds = []  # List of Dockerfile commands.

        if self.specs['base'] is None:
            raise Exception("key `base` is required")

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
        cmd = ("apt-get -y -qq install libxp6 libglu1-mesa gsl-bin libjpeg62-dev libxft-dev")
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
        py_version : str
            Python version (e.g., '3.5.2')
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

        # curl and bzip2 have to be installed for this to work.
        install_cmd = ("curl -sSLO {url}\n"
                       "/bin/bash {file} -b -p /usr/local/miniconda\n"
                       "rm {file}".format(url=install_url, file=install_file))
        # Add Docker RUN command and indent lines.
        install_cmd = indent("RUN", install_cmd, line_suffix=" && \\")

        # Clean this up.
        env_cmd = ("PATH=/usr/local/miniconda/bin:$PATH\n"
                   "PYTHONPATH=/usr/local/miniconda/lib/python{}/site-packages\n"
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

        Parameters
        ----------
        py_pkgs : list
            List of tuple and/or str. Tuples must have two items, the first
            being the name of the package and the second being the version.
            String must be name of package.
        """
        if not self.specs['py_version']:
            raise Exception("Python version must be specified in order to add "
                            "Python packages")

        comment = "# Install Python packages."
        conda_install_list = []
        for item in self.specs['py_pkgs']:
            if isinstance(item, tuple):  # e.g., ('numpy', 1.10)
                # e.g., numpy==1.10
                install_str = "{}=={}".format(item[0], item[1])
                conda_install_list.append(install_str)
            elif isinstance(item, str):  # e.g., 'numpy'
                conda_install_list.append(item)

        add_channel_cmd = "conda config --add channels conda-forge"
        install_cmd = "conda install -y " + ' '.join(conda_install_list)

        cmd = "\n".join((add_channel_cmd, install_cmd))
        cmd = indent("RUN", cmd, line_suffix=" && \\")

        cmd = "\n".join((comment, cmd))
        self._cmds.append(cmd)

    def add_command(self, docker_cmd, cmd, line_suffix):
        """
        docker_cmd : str
            The Docker command (e.g., 'RUN' or 'ENV').
        cmd : str
            Command to be added.
        """
        cmd = indent(docker_cmd, cmd, line_suffix)
        self._cmds.append(cmd)

    def _create(self):
        """Return Dockerfile as string."""
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

    def _save(self):
        """Save Dockerfile."""
        obj = self._create()
        file_path = op.join(self.path, "Dockerfile")
        with open(file_path, 'w') as stream:
            stream.write(obj)
            return

    def build(self):
        """Save Dockerfile and build Docker image from saved Dockerfile."""
        self._save()
        print("Building Docker image")
        image = client.images.build(path=self.path, tag=self.img_name)
        return image



def main():
    env = get_docker_args()

    # Change this so it is not hard-coded.
    d = Dockerfile(d, 'afni-py35', path='samples/afni-py35')
    d._save()  # Save Dockerfile.

    # Build image using saved Dockerfile.
    image = d.build()

    # Run script within Docker container?


if __name__ == "__main__":
    main()
