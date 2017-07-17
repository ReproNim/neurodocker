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


def test_check_url():
    urls = {'good': 'https://www.google.com/',
            '404': 'http://httpstat.us/404',
            'timeout': 'http://10.255.255.255'}

    assert utils.check_url(urls['good']), "Bad response from google.com"
    with pytest.raises(RequestException):
        utils.check_url(urls['404'])
    with pytest.raises(RequestException):
        utils.check_url(urls['timeout'])


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
    import logging

    logger = logging.getLogger(__name__)
    utils.set_log_level(logger, 'info')
    with pytest.raises(ValueError):
        utils.set_log_level(logger, 'fake_level')
