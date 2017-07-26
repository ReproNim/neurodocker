"""Tests for neurodocker.parser"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import pytest

from neurodocker.parser import _SpecsParser


class TestSpecsParser(object):
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test__validate_keys(self):
        # Missing instructions.
        specs = {'pkg_manager': 'apt'}
        with pytest.raises(KeyError):
            _SpecsParser(specs)

        # Missing package manager.
        specs = {'base': 'ubuntu:17.04'}
        with pytest.raises(KeyError):
            _SpecsParser(specs)

        # Invalid top-level key.
        specs = {'pkg_manager': 'apt',
                 'instructions': [('base', 'ubuntu:17.04'),
                                  ('fake_software', 'fake_val')],}
        with pytest.raises(KeyError) as e:
            _SpecsParser(specs)
        assert 'fake_software' in str(e.value)
