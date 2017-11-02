"""Add Dockerfile instructions to install ANTs.

Project repository: https://github.com/stnava/ANTs/

Jakub Kaczmarzyk <jakubk@mit.edu> build several versions on CentOS 5 Docker
images. Those Docker images are located at
https://hub.docker.com/r/kaczmarj/ants/ and the binaries are on Dropbox.
See https://github.com/kaczmarj/ANTs-builds for more information.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from distutils.version import StrictVersion

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import optional_formatter


VERSION_TARBALLS = {"2.2.0": "https://dl.dropbox.com/s/2f4sui1z6lcgyek/ANTs-Linux-centos5_x86_64-v2.2.0-0740f91.tar.gz",
                    "2.1.0": "https://dl.dropbox.com/s/h8k4v6d1xrv0wbe/ANTs-Linux-centos5_x86_64-v2.1.0-78931aa.tar.gz",
                    "2.0.3": "https://dl.dropbox.com/s/oe4v52lveyt1ry9/ANTs-Linux-centos5_x86_64-v2.0.3-c996539.tar.gz",
                    "2.0.0": "https://dl.dropbox.com/s/kgqydc44cc2uigb/ANTs-Linux-centos5_x86_64-v2.0.0-7ae1107.tar.gz",}


class ANTs(BaseInterface):

    _yaml_key = 'ants'
    pretty_name = 'ANTs'

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

        if self.method == 'source':
            try:
                StrictVersion(self.version)
                self.version = "v{}".format(self.version)
            except ValueError:
                pass

        cmd = optional_formatter.format(base_cmd,
                                        binaries_url=binaries_url,
                                        install_deps=deps_cmd,
                                        **self.__dict__)
        return cmd.strip()
