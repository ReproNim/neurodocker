from __future__ import absolute_import, print_function
import argparse
from distutils.version import LooseVersion
import os.path as op

LATEST_PYTHON = "3.6.0"


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



class Dockerfile(object):
    """Dockerfile object.

    Parameters
    ----------
    software : dict
        Software specifications for the Dockerfile. Keys include 'base',
        'py_version', and 'py_pkgs' (so far)
    """
    def __init__(self, software):
        self.software = software
        self._cmds = []  # List of Dockerfile commands.

    def add_base(self):
        """Return Dockerfile command to use the baseimage `base`.

        Parameters
        ----------
        base : str
            The base image and its version (e.g., Ubuntu:16.04). Does the base
            image have to be hosted on Dockerhub?
        """
        cmd = "FROM {}".format(self.software['base'])
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
        py_version = self.software['py_version']
        if py_version is None: return

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
        # cmd = "{}\n{}\n{}\n{}".format(comments[0], install_cmd, comments[1],
        #                              env_cmd, comments[2], conda_python_cmd)
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
        if self.software['py_pkgs'] is None: return

        if not self.software['py_version']:
            raise Exception("Python version must be specified in order to add "
                            "Python packages")

        comment = "# Install Python packages."
        conda_install_list = []
        for item in self.software['py_pkgs']:
            if isinstance(item, tuple):  # e.g., ('numpy', 1.10)
                # e.g., numpy==1.10
                install_str = "{}=={}".format(item[0], item[1])
                conda_install_list.append(install_str)
            elif isinstance(item, str):  # e.g., 'numpy'
                conda_install_list.append(item)

        add_channel_cmd = "conda config --add channels conda-forge"
        install_cmd = "conda install -y " + ' '.join(conda_install_list)

        # cmd = "{}\n{}".format(add_channel_cmd, install_cmd)
        cmd = "\n".join((add_channel_cmd, install_cmd))
        cmd = indent("RUN", cmd, line_suffix=" && \\")

        # cmd = "{}\n{}".format(comment, cmd)
        cmd = "\n".join((comment, cmd))
        self._cmds.append(cmd)

    def add_command(self, cmd):
        """
        cmd : str
            Command to be added.
        """
        self._cmds.append(cmd)

    def create(self):
        """Return Dockerfile as string."""
        return '\n\n'.join(self._cmds)

    def save(self):
        """Save Dockerfile."""
        fname = "Dockerfile"
        obj = self.create()
        with open(fname, 'w') as fp:
            fp.write(obj)



def indent(docker_cmd, text, line_suffix=''):
    """docstring"""
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


def main():
    software = get_docker_args()
    reqs_cmd = ("RUN apt-get update && apt-get install -y bzip2 curl")

    df = Dockerfile(software)
    df.add_base()
    df.add_command(reqs_cmd)
    df.add_miniconda()
    df.add_python_pkgs()
    df.save()


if __name__ == "__main__":
    main()
