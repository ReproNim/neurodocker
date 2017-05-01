"""Tests for neurodocker.parser"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import pytest

from neurodocker.parser import SpecsParser


class TestSpecsParser(object):
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir

    def test_str(self):
        specs = {'base': 'ubuntu:17.04',
                 'pkg_manager': 'yum'}
        assert str(SpecsParser(specs)) == str(specs)

    def test_use_dict_or_json(self):
        import os.path as op
        from neurodocker.utils import save_json
        specs = {'base': 'ubuntu:17.04',
                 'pkg_manager': 'yum'}
        filepath = op.join(self.tmpdir.strpath, 'specs.json')
        save_json(specs, filepath)
        assert SpecsParser(specs).specs == SpecsParser(filepath).specs

    def test__validate_keys(self):
        # Missing base image.
        specs = {'pkg_manager': 'apt'}
        with pytest.raises(KeyError):
            SpecsParser(specs)

        # Missing package manager.
        specs = {'base': 'ubuntu:17.04'}
        with pytest.raises(KeyError):
            SpecsParser(specs)

        # Invalid top-level key.
        specs = {'base': 'ubuntu:17.04',
                 'pkg_manager': 'yum',
                 'fake_software': 'fake_val',}
        with pytest.raises(KeyError) as e:
            SpecsParser(specs)
        assert 'fake_software' in str(e.value)

    def test__parse_conda_pip(self):
        specs_l = {'base': 'ubuntu:17.04',
                   'pkg_manager': 'yum',
                   'miniconda': {'python_version': '3.6.1',
                                 'conda_install': ['nipype', 'numpy'],
                                 'pip_install': ['pandas', 'pylsl']}
                   }
        specs_s = {'base': 'ubuntu:17.04',
                   'pkg_manager': 'yum',
                   'miniconda': {'python_version': '3.6.1',
                                 'conda_install': 'nipype numpy',
                                 'pip_install': 'pandas pylsl'}
                   }
        assert SpecsParser(specs_l).specs == SpecsParser(specs_s).specs
