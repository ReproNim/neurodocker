"""Setup script for neurodocker."""

from setuptools import setup

import versioneer

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()

setup(version=version, cmdclass=cmdclass)
