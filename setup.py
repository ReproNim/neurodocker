#!/usr/bin/env python
from setuptools import setup

setup(name='neurodocker',
      version='dev',
      url='https://github.com/kaczmarj/neurodocker',
      author='Jakub Kaczmarzyk',
      author_email='jakubk@mit.edu',
      packages=['neurodocker'],
      install_requires = ['docker>=2.2.0', 'requests>=2.0.0'],
      )
