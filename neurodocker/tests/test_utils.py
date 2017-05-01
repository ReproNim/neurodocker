"""Tests for neurodocker.utils"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import pytest
from requests.exceptions import RequestException

from neurodocker import utils


def test_manage_pkgs():
    assert 'yum' in utils.manage_pkgs.keys(), "yum not found"
    assert 'apt' in utils.manage_pkgs.keys(), "apt not found"

    # Test that each entry is a dictionary with 'install' and 'remove' keys.
    for manager in utils.manage_pkgs:
        assert 'install' in utils.manage_pkgs[manager].keys(), 'install not found'
        assert 'remove' in utils.manage_pkgs[manager].keys(), 'remove not found'

    assert "yum" not in utils.manage_pkgs['apt'].values()
    assert "apt" not in utils.manage_pkgs['yum'].values()


def test_add_neurodebian():
    os = "xenial"
    full = ("RUN apt-get update -qq && apt-get install -yq --no-install-recommends dirmngr \\\n"
            "    && apt-get clean \\\n"
            "    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \\\n"
            "    && curl -sSL http://neuro.debian.net/lists/xenial.us-nh.full >> /etc/apt/sources.list.d/neurodebian.sources.list \\\n"
            "    && apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9 \\\n"
            "    && apt-get update")
    assert utils.add_neurodebian(os, full=True), "error adding full neurodebian on xenial"

    with pytest.raises(RequestException):
        utils.add_neurodebian('fake_codename', full=False, check_urls=True)

    assert "fake_codename" in utils.add_neurodebian('fake_codename',
                                                    check_urls=False)


def test_check_url():
    urls = {'good': 'https://www.google.com/',
            '404': 'http://httpstat.us/404',
            'timeout': 'http://10.255.255.255'}

    assert utils.check_url(urls['good']), "Bad response from google.com"
    with pytest.raises(RequestException):
        assert not utils.check_url(urls['404']), "404 url returned status < 400"
        assert not utils.check_url(urls['timeout']), "timeout url returned status < 400"


def test_indent():
    pre = "FROM"
    cmd = "centos:latest"
    indented = ' '.join((pre, cmd))
    assert utils.indent(pre, cmd) == indented, "error prepending Dockerfile instruction"

    pre = "RUN"
    cmd = ("echo 'green eggs'\n"
           "&& echo ' and'\n"
           "&& echo ' ham'")
    indented = ("RUN echo 'green eggs' \\\n"
                "    && echo ' and' \\\n"
                "    && echo ' ham'")
    assert utils.indent(pre, cmd) == indented, "error indenting multi-line instruction"


def test_save_load_json(tmpdir):
    filepath = tmpdir.join('test.json').strpath

    obj = {'foo': 'bar'}
    utils.save_json(obj, filepath)

    loaded = utils.load_json(filepath)
    assert obj == loaded


def test_set_log_level(tmpdir):
    utils.set_log_level('info')
    with pytest.raises(ValueError):
        utils.set_log_level('fake_level')
