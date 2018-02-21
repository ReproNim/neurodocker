"""Tests for neurodocker.utils"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import pytest

from neurodocker import utils


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
