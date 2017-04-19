"""Tests for src.docker.ants.ANTs"""
from __future__ import absolute_import, division, print_function

import pytest

from neurodocker.interfaces import ANTs


class TestANTs(object):
    """Tests for ANTs class."""
    def install_binaries_apt(self):
        # --- Version 2.1.0 ---
        # apt
        url = "https://www.dropbox.com/s/x7eyk125bhwiisu/ants-2.1.0_centos-5.tar.gz?dl=1"
        test = ("#-------------------\n"
                "# Install ANTs 2.1.0\n"
                "#-------------------\n"
                "WORKDIR /opt\n"
                "RUN deps='ca-certificates wget' \\\n"
                "    && apt-get update -qq && apt-get install -yq --no-install-recommends $deps \\\n"
                "    && wget -qO ants.tar.gz {url} \\\n"
                "    && tar xzf ants.tar.gz \\\n"
                "    && rm -f ants.tar.gz \\\n"
                "    && apt-get purge -y --auto-remove $deps\n"
                "ENV ANTSPATH=/opt/ants\n"
                "ENV PATH=$ANTSPATH:$PATH".format(url=url))
        ants = ANTs(version='2.1.0', pkg_manager='apt', use_binaries=True)
        assert ants.cmd == test, "command to install ANTs binaries not correct (apt)"

        # yum
        url = "https://www.dropbox.com/s/x7eyk125bhwiisu/ants-2.1.0_centos-5.tar.gz?dl=1"
        test = ("#-------------------\n"
                "# Install ANTs 2.1.0\n"
                "#-------------------\n"
                "WORKDIR /opt\n"
                "RUN deps='ca-certificates wget' \\\n"
                "    && yum install -y -q $deps \\\n"
                "    && wget -qO ants.tar.gz {url} \\\n"
                "    && tar xzf ants.tar.gz \\\n"
                "    && rm -f ants.tar.gz \\\n"
                "    && yum autoremove -y -q\n"
                "ENV ANTSPATH=/opt/ants\n"
                "ENV PATH=$ANTSPATH:$PATH".format(url=url))
        ants = ANTs(version='2.1.0', pkg_manager='yum', use_binaries=True)
        assert ants.cmd == test, "command to install ANTs binaries not correct (yum)"

        # --- next version ---
        # apt
        # yum

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
