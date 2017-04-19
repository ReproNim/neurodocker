"""Tests for neurodocker.parser"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import
import os

import pytest

from neurodocker.parser import SpecsParser


class TestSpecsParser(object):

    def test_init(self):
        specs = {'base': 'ubuntu:16.04',
                 'conda_env': {'conda_install': ['traits'],
                               'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz'],
                               'python_version': '3.5.1'},
                 'software': {'ants': {'use_binaries': True, 'version': '2.1.0'},
                              'fsl': {'use_binaries': True, 'version': '5.0.8'}}}
        parser = SpecsParser(specs=specs)

        correct = {'base': 'ubuntu:16.04',
                   'conda_env': {'conda_install': 'traits',
                                 'pip_install': 'https://github.com/nipy/nipype/archive/master.tar.gz',
                                 'python_version': '3.5.1'},
                    'software': {'ants': {'use_binaries': True, 'version': '2.1.0'},
                                 'fsl': {'use_binaries': True, 'version': '5.0.8'}}}

        assert parser.specs == correct, "error parsing environment specs"
