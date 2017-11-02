"""Add Dockerfile instructions to install Convert3D (C3D).

Project repository: https://sourceforge.net/projects/c3d/
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import optional_formatter

VERSION_TARBALLS = {
    "nightly": "https://sourceforge.net/projects/c3d/files/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz/download",
    "1.0.0": "https://sourceforge.net/projects/c3d/files/c3d/1.0.0/c3d-1.0.0-Linux-x86_64.tar.gz/download",
}


class Convert3D(BaseInterface):

    _yaml_key = 'convert3d'
    pretty_name = 'Convert3D'

    def __init__(self, version, method='binaries', **kwargs):
        self.version = version
        self.method = method
        self.__dict__.update(kwargs)

        super().__init__(yaml_key=self._yaml_key,
                         version=version,
                         method=method,
                         **kwargs)

    def _create_cmd(self):
        base_cmd = self._specs['instructions']
        binaries_url = VERSION_TARBALLS.get(self.version, None)
        if self.method == 'binaries' and binaries_url is None:
            err = "{} binaries not available for version '{}'"
            raise ValueError(err.format(self.pretty_name, self.version))

        deps_cmd = self._get_install_deps_cmd()

        cmd = optional_formatter.format(base_cmd,
                                        binaries_url=binaries_url,
                                        install_deps=deps_cmd,
                                        **self.__dict__)
        return cmd
