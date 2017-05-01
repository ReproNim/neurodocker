#!/usr/bin/env python
from setuptools import find_packages, setup

setup(name='neurodocker',
      version='dev',
      url='https://github.com/kaczmarj/neurodocker',
      author='Jakub Kaczmarzyk',
      author_email='jakubk@mit.edu',
      packages=find_packages(),
      install_requires = ['docker>=2.2.0', 'requests>=2.0.0'],
      )
