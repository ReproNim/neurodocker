"""Tests for neurodocker.interfaces.ANTs"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from io import BytesIO

import pytest

from neurodocker.docker_api import Dockerfile, DockerImage, DockerContainer
from neurodocker.parser import SpecsParser
from neurodocker.interfaces import ANTs


class TestANTs(object):
    """Tests for ANTs class."""
    def install_binaries_centos7(self):
        """Install ANTs 2.1.0 binaries on Ubuntu."""
        specs = {'base': 'centos:7',
                 'software': {
                     'ants': {'version': '2.1.0', 'use_binaries': True}}}
        parser = SpecsParser(specs=specs)
        cmd = Dockerfile(specs=parser.specs, pkg_manager='yum').cmd
        fileobj = BytesIO(cmd.encode('utf-8'))

        image = DockerImage(fileobj=fileobj).build_raw()
        container = DockerContainer(image)
        container.start()
        output = container.exec_run('Atropos')
        assert "error" not in output, "error running bet"
        container.cleanup(remove=True, force=True)

    def test_build_from_source_github(self):
        # --- latest version (master branch) ---
        # apt
        test = ("#-------------------\n"
                "# Install ANTs latest\n"
                "#-------------------\n"
                "WORKDIR /tmp/ants-build\n"
                "RUN deps='ca-certificates cmake g++ gcc git make zlib1g-dev' \\\n"
                "    && apt-get update -qq && apt-get install -yq --no-install-recommends $deps \\\n"
                "    && git clone https://github.com/stnava/ANTs.git \\\n"
                "    && cd ANTs \\\n"
                "    && cd .. && mkdir build && cd build \\\n"
                "    && cmake ../ANTs && make -j 2 \\\n"
                "    && mkdir -p /opt/ants \\\n"
                "    && mv bin/* /opt/ants && mv ../ANTs/Scripts/* /opt/ants \\\n"
                "    && cd /tmp && rm -rf ants-build \\\n"
                "    && apt-get purge -y --auto-remove $deps\n"
                "ENV ANTSPATH=/opt/ants\n"
                "ENV PATH=$ANTSPATH:$PATH")
        ants = ANTs(version='latest', pkg_manager='apt', use_binaries=False)
        assert ants.cmd == test, "command to compile ANTs not correct (apt)"

        # yum
        test = ("#-------------------\n"
                "# Install ANTs latest\n"
                "#-------------------\n"
                "WORKDIR /tmp/ants-build\n"
                "RUN deps='ca-certificates cmake gcc-c++ git make zlib-devel' \\\n"
                "    && yum install -y -q $deps \\\n"
                "    && git clone https://github.com/stnava/ANTs.git \\\n"
                "    && cd ANTs \\\n"
                "    && cd .. && mkdir build && cd build \\\n"
                "    && cmake ../ANTs && make -j 2 \\\n"
                "    && mkdir -p /opt/ants \\\n"
                "    && mv bin/* /opt/ants && mv ../ANTs/Scripts/* /opt/ants \\\n"
                "    && cd /tmp && rm -rf ants-build \\\n"
                '    && yum remove -y -q $(echo "$deps" | sed "s/ca-certificates//g")\n'
                "ENV ANTSPATH=/opt/ants\n"
                "ENV PATH=$ANTSPATH:$PATH")
        ants = ANTs(version='latest', pkg_manager='yum', use_binaries=False)
        assert ants.cmd == test, "command to compile ANTs not correct (yum)"
