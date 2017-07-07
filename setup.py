#!/usr/bin/env python

import os
from setuptools import find_packages, setup

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

def _get_version(filepath):
    """Return version string."""
    with open(filepath, 'r') as fp:
        return fp.read().strip()

version_file = os.path.join(BASE_PATH, "neurodocker", "VERSION")
__version__ = _get_version(version_file)


setup(name='neurodocker',
      version=__version__,
      url='https://github.com/kaczmarj/neurodocker',
      author='Jakub Kaczmarzyk',
      author_email='jakubk@mit.edu',
      packages=find_packages(),
      package_data={'': [version_file]},
      include_package_data=True,
      install_requires = [
         'requests>=2.0',
         'docker>=2.3'
      ],
      entry_points={'console_scripts':
                    ['neurodocker=neurodocker.neurodocker:main']}
      )
