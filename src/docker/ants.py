"""Class to add ANTs.

Project repository: https://github.com/stnava/ANTs/

ANTs recommends building from source. Versions 2.0.0 and newer are available
on GitHub, and older versions are available on SourceForge.

Build instructions (takes approximately 40 minutes):
https://github.com/stnava/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS

When building ANTs versions 2.0.1 and 2.1.0, ITK build broke because of gcc
(version 5.x?). Getting an older version of gcc (4.9) fixed that issue.

How to install gcc-4.9 on Ubuntu and Debian:

    # ----- UBUNTU -----
    # Get version codename.
    . /etc/os-release
    UBUNTU_CODENAME=$(echo "$VERSION" | grep -o '\<[A-Z][a-z]*\>' | awk 'NR==1{print $1}' | awk '{print tolower($0)}')
    # Add PPA with gcc-4.9
    echo "deb http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu $UBUNTU_CODENAME main" >> /etc/apt/sources.list
    echo "deb-src http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu $UBUNTU_CODENAME main" >> /etc/apt/sources.list
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BA9EF27F
    apt-get update

    # ----- DEBIAN ----- (non-jessie)
    # http://stackoverflow.com/a/29729834/5666087
    # Get version codename. Does not work on Debian 6 (/etc/os-release does not exist).
    . /etc/os-release
    DEBIAN_CODENAME=$(echo "$VERSION" | grep -o '\<[a-z]*\>')
    # Update apt to find Debian jessie packages.
    apt-get update
    cp /etc/apt/sources.list /etc/apt/sources.list.ORIGINAL
    sed -i -- 's/${DEBIAN_CODENAME}/jessie/g' /etc/apt/sources.list
    apt-get update
    apt-get install gcc-4.9 g++-4.9
    cp /etc/apt/sources.list.ORIGINAL /etc/apt/sources.list
    apt-get update


Dockerfile commands to build ANTs from source on Ubuntu 16.04:

    #-------------
    # Install ANTs
    #-------------
    RUN apt-get update -qq && \
        apt-get install -yq --no-install-recommends \
        ca-certificates \
        cmake \
        gcc-4.9 \
        g++-4.9 \
        git \
        make \
        zlib1g-dev && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

    RUN ln -s /usr/bin/gcc-4.9 /usr/bin/cc && \
        ln -s /usr/bin/gcc-4.9 /usr/bin/gcc && \
        ln -s /usr/bin/g++-4.9 /usr/bin/g++ && \
        ln -s /usr/bin/g++-4.9 /usr/bin/c++

    WORKDIR /tmp
    RUN git clone git://github.com/stnava/ANTs.git &&  \
        cd ANTs &&  \
        # ANTs 2.1.0
        git checkout 78931aa6c4943af25e0ee0644ac611d27127a01e &&  \
        mkdir build && cd build && cmake .. && make -j 2 &&  \
        mkdir -p /opt/ants &&  \
        cp bin/* /opt/ants && cp ../Scripts/* /opt/ants &&  \
        cd /tmp && rm -rf ANTs
    ENV ANTSPATH=/opt/ants/ \
        PATH=/opt/ants:$PATH
"""
from __future__ import absolute_import, division, print_function

from src.docker.utils import indent
from src.utils import logger


def _get_dependencies_ubuntu(pkgs):
    """Get ANTs build dependencies on Ubuntu.

    Parameters
    ----------
    pkgs : list, tuple
        Packages to install using apt-get.

    Returns
    -------
    instruction : str
        Dockerfile instruction to install ANTs build dependencies.
    """
    comment = "# Install gcc-4.9, g++-4.9, and other dependencies."
    # Get Ubuntu version codename (e.g., xenial).
    get_codename = (". /etc/os-release &&\n"
                    "UBUNTU_CODENAME=$(echo \"$VERSION\" "
                    "| grep -o '\<[A-Z][a-z]*\>' "
                    "| awk 'NR==1{print $1}' "
                    "| awk '{print tolower($0)}')")
    get_codename = indent("RUN", get_codename)
    # Add PPA that contains gcc-4.9.
    ppa_url = "http://ppa.launchpad.net/ubuntu-toolchain-r/test/ubuntu"
    ppa_key = "BA9EF27F"
    add_ppa = ('echo "deb {url} $UBUNTU_CODENAME main" >> /etc/apt/sources.list &&\n'
               'echo "deb-src {url} $UBUNTU_CODENAME main" >> /etc/apt/sources.list &&\n'
               "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {key} &&\n"
               "apt-get update -qq".format(url=ppa_url, key=ppa_key))
    # Install all dependencies
    pkgs_str = '\n'.join(pkgs)
    install_pkgs = ("&& apt-get install -yq --no-install-recommends\n{}"
                    "".format(pkgs_str))
    cleanup = ("&& apt-get clean &&\n"
               "rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*")
    full_install_cmd = '\n'.join((add_ppa, install_pkgs, cleanup))
    full_install_cmd = indent("RUN", full_install_cmd)

    symlinks = ("ln -s /usr/bin/gcc-4.9 /usr/bin/cc &&\n"
                "ln -s /usr/bin/gcc-4.9 /usr/bin/gcc &&\n"
                "ln -s /usr/bin/g++-4.9 /usr/bin/g++ &&\n"
                "ln -s /usr/bin/g++-4.9 /usr/bin/c++")
    symlinks = indent("RUN", symlinks)

    return '\n'.join((comment, get_codename, full_install_cmd, symlinks))


def _get_dependencies_debian(pkgs):
    """Get ANTs build dependencies on Debian.

    Parameters
    ----------
    pkgs : list, tuple
        Packages to install using apt-get.

    Returns
    -------
    instruction : str
        Dockerfile instruction to install ANTs build dependencies.
    """
    gcc_comment = "# Install gcc-4.9 and g++-4.9 from jessie package repository"
    # Get Debian version codename (e.g., wheezy).
    get_codename = (". /etc/os-release &&\n"
                    "DEBIAN_CODENAME=$(echo \"$VERSION\" "
                    "| grep -o '\<[a-z]*\>')")
    get_codename = indent("RUN", get_codename)
    # Install gcc-4.9 and g++-4.9 from jessie package repository.
    workdir = "WORKDIR /etc/apt"
    install_gcc = ("apt-get update &&\n"
                   "cp sources.list sources.list.ORIGINAL &&\n"
                   "sed -i -- 's/${DEBIAN_CODENAME}/jessie/g' sources.list &&\n"
                   "apt-get update &&\n"
                   "apt-get install gcc-4.9 g++-4.9 &&\n"
                   "cp sources.list.ORIGINAL sources.list &&\n"
                   "apt-get update")
    # Install packages other than gcc and g++.
    pkgs = [p for p in pkgs if "gcc" not in p and "g++" not in p]
    pkgs_str = '\n'.join(pkgs)
    install_pkgs = ("&& apt-get install -yq --no-install-recommends\n{}"
                    "".format(pkgs_str))
    cleanup = ("&& apt-get clean &&\n"
               "rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*")
    full_install_cmd = '\n'.join(install_gcc, install_pkgs, cleanup)
    install_pkgs = indent("RUN", full_install_cmd)
    symlinks = ("ln -s /usr/bin/gcc-4.9 /usr/bin/cc &&\n"
                "ln -s /usr/bin/gcc-4.9 /usr/bin/gcc &&\n"
                "ln -s /usr/bin/g++-4.9 /usr/bin/g++ &&\n"
                "ln -s /usr/bin/g++-4.9 /usr/bin/c++")
    symlinks = indent("RUN", symlinks)

    return '\n'.join((gcc_comment, get_codename, workdir, install_pkgs,
                      symlinks))


class ANTs(object):
    """Add Dockerfile instructions to install ANTs. Versions 2.0.0+ are
    supported.

    Inspired by the Dockerfile at https://hub.docker.com/r/nipype/workshops/
    `docker pull nipype/workshops:latest-nofsspm`
    """
    VERSION_HASHES = {"latest": None,
                      "2.1.0": "78931aa6c4943af25e0ee0644ac611d27127a01e",
                      "2.1.0rc3": "465cc8cdf0f8cc958edd2d298e05cc2d7f8a48d8",
                      "2.1.0rc2": "17160f72f5e1c9d6759dd32b7f2dc0b36ded338b",
                      "2.1.0rc1": "1593a7777d0e6c8be0b9462012328bde421510b9",
                      "2.0.3": "c9965390c1a302dfa9e63f6ca3cb88f68aab329f",
                      "2.0.2": "7b83036c987e481b2a04490b1554196cb2fc0dab",
                      "2.0.1": "dd23c394df9292bae4c5a4ece3023a7571791b7d",
                      "2.0.0": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",
                      "HoneyPot": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",}

    BUILD_DEPENDENCIES = {"centos": ['ca-certificates', 'cmake', 'g++', 'git',
                                     'make', 'zlib-devel'],
                          "debian": ['ca-certificates', 'cmake', 'gcc-4.9',
                                     'g++-4.9', 'git', 'make', 'zlib1g-dev'],
                          "ubuntu": ['ca-certificates', 'cmake', 'gcc-4.9',
                                     'g++-4.9', 'git', 'make', 'zlib1g-dev'],}

    def __init__(self, version, os):
        self.version = version
        self.os = os

        valid_ants_versions = ANTs.VERSION_HASHES.keys()
        if self.version not in valid_ants_versions:
            raise ValueError("ANTs version not supported. Supported versions "
                             "are {}.".format(', '.join(valid_ants_versions)))
        valid_operating_systems = ANTs.BUILD_DEPENDENCIES.keys()
        if self.os not in valid_operating_systems:
            raise ValueError("Operating system not supported.")

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """"""
        comment = ("#-------------------\n"
                   "# Install ANTs {}\n"
                   "#-------------------".format(self.version))
        chunks = [comment, self.get_dependencies(),
                  self.build_from_source_github()]
        return "\n".join(chunks)

    def get_dependencies(self):
        """Return Dockerfile instructions to install build dependencies."""
        deps = ANTs.BUILD_DEPENDENCIES[self.os]
        deps = sorted(deps)
        
        if self.os == "ubuntu":
            cmd = _get_dependencies_ubuntu(deps)

        elif self.os == "debian":
            cmd = _get_dependencies_debian(deps)

        elif self.os == 'centos':
            cmd = ("yum -y install\n"
                   "{} &&\n"
                   "yum clean packages &&\n"
                   "rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*".format(deps))
            cmd = indent("RUN", cmd)

        return cmd

    def build_from_source_github(self):
        """Return Dockerfile instructions to build ANTs from source hosted on
        GitHub (https://github.com/stnava/ANTs).
        """
        version_hash = ANTs.VERSION_HASHES[self.version]
        workdir_cmd = "WORKDIR /tmp"

        if self.version == "latest":
            checkout = ""
        else:
            checkout = "git checkout {} && \n".format(version_hash)

        cmd = ("git clone https://github.com/stnava/ANTs.git && \n"
               "cd ANTs && \n"
               "{}"
               "mkdir build && cd build && cmake .. && make && \n"
               "mkdir -p /opt/ants && \n"
               "cp bin/* /opt/ants && cp ../Scripts/* /opt/ants && \n"
               "cd /tmp && rm -rf ANTs".format(checkout))
        cmd = indent("RUN", cmd)

        env_cmd = ("ANTSPATH=/opt/ants/\n"
                   "PATH=/opt/ants:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((workdir_cmd, cmd, env_cmd))
