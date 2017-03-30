"""Class to add ANTs.

Project repository: https://github.com/stnava/ANTs/

ANTs recommends building from source. Versions 2.0.0 and newer are available
on GitHub, and older versions are available on SourceForge.

Build instructions (takes approximately 40 minutes):
https://github.com/stnava/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS

When building ANTs versions 2.0.1 and 2.1.0, ITK build broke because of gcc
(version 5.x?). Getting an older version of gcc (4.9) fixed that issue.

Dockerfile commands to build ANTs from source on Ubuntu 16.04:

    #-------------
    # Install ANTs
    #-------------
    RUN apt-get update -qq && \
        add-apt-repository ppa:ubuntu-toolchain-r/test && apt-get update && \
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
        deps = "\n".join(deps)
        if self.os in ['debian', 'ubuntu']:
            cmd = ("apt-get update -qq &&\n"
                   "add-apt-repository ppa:ubuntu-toolchain-r/test &&\n"
                   "apt-get update &&\n"
                   "apt-get install -yq --no-install-recommends\n"
                   "{} &&\n"
                   "apt-get clean &&\n"
                   "rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*".format(deps))
            symlinks = ("ln -s /usr/bin/gcc-4.9 /usr/bin/cc &&\n"
                        "ln -s /usr/bin/gcc-4.9 /usr/bin/gcc &&\n"
                        "ln -s /usr/bin/g++-4.9 /usr/bin/g++ &&\n"
                        "ln -s /usr/bin/g++-4.9 /usr/bin/c++")
            cmd = indent("RUN", cmd)
            symlinks = indent("RUN", symlinks)
            cmd = "\n".join((cmd, symlinks))

        elif self.os in ['centos']:
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
