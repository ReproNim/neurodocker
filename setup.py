#!/usr/bin/env python

import os
from setuptools import find_packages, setup


def main():
    here = os.path.dirname(os.path.realpath(__file__))

    # https://github.com/nipy/nipype/blob/master/setup.py#L114-L120
    ldict = locals()
    version_file = os.path.join(here, 'neurodocker', 'version.py')
    with open(version_file) as fp:
        exec(fp.read(), globals(), ldict)

    reqs_file = os.path.join(here, 'requirements.txt')
    with open(reqs_file) as fp:
        requirements = [r.strip() for r in fp.readlines()]

    setup(name='neurodocker',
          version=ldict['__version__'],
          url='https://github.com/kaczmarj/neurodocker',
          author='Jakub Kaczmarzyk',
          author_email='jakubk@mit.edu',
          license='Apache License, 2.0',
          packages=find_packages(),
          install_requires = requirements,
          entry_points={'console_scripts':
                        ['neurodocker=neurodocker.neurodocker:main']}
          )

if __name__ == '__main__':
    main()
