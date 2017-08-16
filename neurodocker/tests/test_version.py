"""Tests for neurodocker.utils"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import shutil

from neurodocker import version


def test_get_gitversion():
    gitver = version.get_gitversion()

    if shutil.which('git') is not None:  # git exists
        assert gitver is not None
        if gitver.startswith('v'):
            assert gitver[1:] == version.__version__
        else:
            assert gitver == version.__version__
    else:
        assert version.__version__
