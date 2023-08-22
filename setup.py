"""Setup script for neurodocker."""

import versioneer
from setuptools import setup

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()

setup(version=version, cmdclass=cmdclass)
