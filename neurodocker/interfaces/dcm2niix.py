"""Add Dockerfile instructions to install dcm2niix.

Project repository: https://github.com/rordenlab/dcm2niix
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from urllib.parse import urljoin

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import optional_formatter


class Dcm2niix(BaseInterface):

    _yaml_key = 'dcm2niix'
    pretty_name = 'dcm2niix'

    def __init__(self, version, method='source', **kwargs):
        self.version = version
        self.method = method
        self.__dict__.update(kwargs)

        super().__init__(yaml_key=self._yaml_key,
                         version=version,
                         method=method,
                         **kwargs)

    def _create_cmd(self):
        base_cmd = self._specs['instructions']
        deps_cmd = self._get_install_deps_cmd()

        source_url = "https://github.com/rordenlab/dcm2niix/tarball"
        if self.version == 'latest':
            source_url = urljoin(source_url, 'master')
        else:
            source_url = urljoin(source_url, self.version)

        cmd = optional_formatter.format(base_cmd,
                                        install_deps=deps_cmd,
                                        source_url=source_url,
                                        **self.__dict__)
        return cmd
