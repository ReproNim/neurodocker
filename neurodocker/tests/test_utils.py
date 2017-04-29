"""Tests for neurodocker.utils"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import pytest
from requests.exceptions import RequestException

from neurodocker.utils import add_neurodebian, check_url, indent, manage_pkgs


def test_manage_pkgs():
    assert 'yum' in manage_pkgs.keys(), "yum not found"
    assert 'apt' in manage_pkgs.keys(), "apt not found"

    # Test that each entry is a dictionary with 'install' and 'remove' keys.
    for manager in manage_pkgs:
        assert 'install' in manage_pkgs[manager].keys(), 'install not found'
        assert 'remove' in manage_pkgs[manager].keys(), 'remove not found'

    assert "yum" not in manage_pkgs['apt'].values()
    assert "apt" not in manage_pkgs['yum'].values()


def test_check_url():
    urls = {'good': 'https://www.google.com/',
            '404': 'http://httpstat.us/404',
            'timeout': 'http://10.255.255.255'}

    assert check_url(urls['good']), "Bad response from google.com"
    with pytest.raises(RequestException):
        assert not check_url(urls['404']), "404 url returned status < 400"
        assert not check_url(urls['timeout']), "timeout url returned status < 400"


def test_indent():
    pre = "FROM"
    cmd = "centos:latest"
    indented = ' '.join((pre, cmd))
    assert indent(pre, cmd) == indented, "error prepending Dockerfile instruction"

    pre = "RUN"
    cmd = ("echo 'green eggs'\n"
           "&& echo ' and'\n"
           "&& echo ' ham'")
    indented = ("RUN echo 'green eggs' \\\n"
                "    && echo ' and' \\\n"
                "    && echo ' ham'")
    assert indent(pre, cmd) == indented, "error indenting multi-line instruction"


def test_add_neurodebian():
    os = "xenial"
    full = ("RUN apt-get update -qq && apt-get install -yq --no-install-recommends dirmngr \\\n"
            "    && apt-get clean \\\n"
            "    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \\\n"
            "    && curl -sSL http://neuro.debian.net/lists/xenial.us-nh.full >> /etc/apt/sources.list.d/neurodebian.sources.list \\\n"
            "    && apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9 \\\n"
            "    && apt-get update")
    assert add_neurodebian(os, full=True), "error adding full neurodebian on xenial"

    os = "fakeos"
    libre = ("RUN apt-get update -qq && apt-get install -yq --no-install-recommends dirmngr \\\n"
             "    && apt-get clean \\\n"
             "    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \\\n"
             "    && curl -sSL http://neuro.debian.net/lists/fakeos.us-nh.libre >> /etc/apt/sources.list.d/neurodebian.sources.list \\\n"
             "    && apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9 \\\n"
             "    && apt-get update")
    with pytest.raises(RequestException):
        add_neurodebian(os, full=False)
        assert add_neurodebian(os, full=False) == libre, "error adding libre neurodebian on fakeos"
