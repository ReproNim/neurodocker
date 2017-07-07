#!/usr/bin/env python

from setuptools import find_packages, setup

import neurodocker

setup(name='neurodocker',
      version=neurodocker.__version__,
      url='https://github.com/kaczmarj/neurodocker',
      author='Jakub Kaczmarzyk',
      author_email='jakubk@mit.edu',
      packages=find_packages(),
      install_requires = [
         'requests>=2.0',
         'docker>=2.3'
      ],
      entry_points={'console_scripts':
                    ['neurodocker=neurodocker.neurodocker:main']}
      )
