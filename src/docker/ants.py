"""Class to add ANTs.

Project repository: https://github.com/stnava/ANTs/

Binaries for versions 2.0.0 and newer are available in the GitHub repository,
(and older versions are available on SourceForge), but ANTs recommends building
from source.

Build instructions:
https://github.com/stnava/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS

Dockerfile commands to build ANTs from source:

    FROM ubuntu:16.04
    RUN apt-get update && apt-get install -y cmake g++ git zlib1g-dev
    RUN git clone git://github.com/stnava/ANTs.git && \
        mkdir antsbin && \
        cd antsbin && \
        cmake ../ANTs && \
        make -j 2
    ENV ANTSPATH=/antsbin/bin/
    ENV PATH=$ANTSPATH:$PATH


Dockerfile commands to download ANTs binaries:

    FROM ubuntu:16.04
    RUN apt-get update && apt-get install -y bzip2 curl
    RUN curl -LO <URL> && \
        tar zxvf <TARBALL>
    ENV PATH=/path/to/ants/bin:$PATH
"""
from __future__ import absolute_import, division, print_function

from .utils import indent
from ..utils import logger, check_url


class ANTs(object):
    """Class to add ANTs installation to Dockerfile. Versions 2.0.0 and newer
    are available on GitHub. Previous versions are available on SourceForge.

    Parameters
    ----------
    version : str
        ANTs version to use.
    os : {'Centos', 'Debian', 'RedHat', 'Ubuntu'}
        Operating system.
    """
    def __init__(self, version, os=None):
        self.version = version
        self.os = os
        self._check_version()

        if self.os is not None:
            self.os = self.os.lower()
            if self.os not in ['centos', 'debian', 'redhat', 'ubuntu']:
                raise ValueError("Invalid operating system")

        self.deps = ['bzip2', 'ca-certificates', 'curl']

        # Dependencies to build from source.
        self.deps_for_source = {
            "centos": ['cmake', 'g++', 'git', 'zlib-devel'],
            "debian": ['cmake', 'g++', 'git', 'zlib1g-dev'],
            "redhat": ['cmake', 'g++', 'git', 'zlib-devel'],
            "ubuntu": ['cmake', 'g++', 'git', 'zlib1g-dev']
        }

    def _check_version(self):
        """Raise ValueError if version is invalid."""
        version_split = self.version.split('.')
        # Check that major and minor version numbers are integers.
        try:
            version_split[0] = int(version_split[0])
            version_split[1] = int(version_split[1])
        except ValueError:
            raise ValueError("Invalid version.")

    def _add_version_2_1_0(self):
        """Return Dockerfile instructions to install ANTs 2.1.0. Uses binaries
        from GitHub."""
        base_url = "https://github.com/stnava/ANTs/releases/download/v2.1.0/"
        install_files = {
            "centos": "Linux_X_64.tar.bz2.RedHat",
            "debian": "Linux_Debian_jessie_x64.tar.bz2",
            "redhat": "Linux_X_64.tar.bz2.RedHat",
            "ubuntu": "Linux_Ubuntu14.04.tar.bz2"
        }
        install_file = install_files[self.os]
        install_url = base_url + install_file

        download_cmd = ("curl -LO {url}\n"
                        "mkdir ants-2.1.0\n"
                        "tar jxvf {file} -C ants-2.1.0 --strip-components 1\n"
                        "rm -f {file}"
                        "".format(url=install_url, file=install_file))
        download_cmd = indent("RUN", download_cmd, " && \\")
        env_cmd = ("ENV PATH=/ants-2.1.0:$PATH")
        return "\n".join((download_cmd, env_cmd))

    def _add_version_1_9_x(self):
        """Return Dockerfile instructions to install ANTs 1.9.x. Uses binaries
        from SourceForge."""
        base_url = "https://sourceforge.net/projects/advants/files/ANTS/ANTS_1_9_x/"
        install_file = "ANTs-1.9.x-Linux.tar.gz"
        install_url = base_url + install_file

        download_cmd = ("curl -LO {url}\n"
                        "tar zxvf {file}\n"
                        "rm {file}".format(url=install_url, file=install_file))
        download_cmd = indent("RUN", download_cmd, " && \\")
        env_cmd = ("ENV PATH=/ANTs-1.9.x-Linux/bin:$PATH")
        return "\n".join((download_cmd, env_cmd))
