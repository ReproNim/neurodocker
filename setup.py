#!/usr/bin/env python

from setuptools import find_packages, setup

setup(name='neurodocker',
      version='0.1.0.dev0',
      url='https://github.com/kaczmarj/neurodocker',
      author='Jakub Kaczmarzyk',
      author_email='jakubk@mit.edu',
      packages=find_packages(),
      install_requires = [
         'requests',
         'docker>=2.3'
      ],
      entry_points={'console_scripts':
                    ['neurodocker=neurodocker.main:main']}
      )
