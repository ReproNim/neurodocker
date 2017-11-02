"""Add Dockerfile instructions to install AFNI.

Homepage: https://afni.nimh.nih.gov/
GitHub repo: https://github.com/afni/afni
Documentation: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/index.html

Notes
-----
- AFNI uses something like semantic versioning starting from 15.3.00, released
  on GitHub on January 4, 2016. Before this, it is unclear how AFNI was
  versioned.
- Only the latest binaries exist on AFNI's website.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from distutils.version import StrictVersion

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import optional_formatter


VERSION_TARBALLS = {
    "latest": "https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz",
    "17.2.02": "https://dl.dropbox.com/s/yd4umklaijydn13/afni-Linux-openmp64-v17.2.02.tgz",
}


class AFNI(BaseInterface):

    _yaml_key = 'afni'
    pretty_name = 'AFNI'

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
                self.version = "AFNI_{}".format(self.version)
            except ValueError:
                pass

        cmd = optional_formatter.format(base_cmd,
                                        binaries_url=binaries_url,
                                        install_deps=deps_cmd,
                                        **self.__dict__)
        return cmd.strip()
