"""Tests for src.docker.ants.ANTs"""
from __future__ import absolute_import, division, print_function

import pytest

from src.docker.ants import ANTs, manage_pkgs

def test_manage_pkgs():
    assert 'yum' in manage_pkgs.keys(), "yum not found"
    assert 'apt' in manage_pkgs.keys(), "apt not found"

    # Test that each entry is a dictionary with 'install' and 'remove' keys.
    for manager in manage_pkgs:
        assert 'install' in manage_pkgs[manager].keys(), 'install not found'
        assert 'remove' in manage_pkgs[manager].keys(), 'remove not found'

    assert "yum" not in manage_pkgs['apt'].values()
    assert "apt" not in manage_pkgs['yum'].values()


class TestANTs(object):
    """Tests for ANTs class."""
    def install_binaries_apt(self):
        # Version
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

    def install_binaries_yum(self):
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

    # def test_build_from_source_github(self):
    #     pass
