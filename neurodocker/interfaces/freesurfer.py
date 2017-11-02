"""Add Dockerfile instructions to install FreeSurfer.

Project repository: https://github.com/freesurfer/freesurfer
Project website: https://surfer.nmr.mgh.harvard.edu/
Project wiki: https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferWiki
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import optional_formatter


class FreeSurfer(BaseInterface):

    _yaml_key = 'freesurfer'
    pretty_name = 'FreeSurfer'

    def __init__(self, version, method='binaries', min=False,
                 license_path=None, **kwargs):
        self.version = version
        self.method = method
        self.min = min
        self.license_path = license_path
        self.__dict__.update(kwargs)

        if self.min:
            self.version = "{}-min-recon-all".format(self.version)

        super().__init__(yaml_key=self._yaml_key,
                         version=self.version,
                         method=self.method,
                         **kwargs)

    def _create_cmd(self):
        base_cmd = self._specs['instructions'].strip()

        if not self.min:
            self.binaries_url = _get_binaries_url(self.version)
            if self.method == 'binaries' and self.binaries_url is None:
                err = "{} binaries not available for version '{}'"
                raise ValueError(err.format(self.pretty_name, self.version))

        deps_cmd = self._get_install_deps_cmd()

        if self.license_path is not None:
            base_cmd += '\n' + self._copy_license()

        cmd = optional_formatter.format(base_cmd,
                                        install_deps=deps_cmd,
                                        **self.__dict__)
        return cmd

    def _copy_license(self):
        """Return command to copy local license file into the container. Path
        must be a relative path within the build context.
        """
        import os

        if os.path.isabs(self.license_path):
            raise ValueError("Path to license file must be relative, but "
                             "absolute path was given.")

        comment = "# Copy license file into image."
        cmd = 'COPY ["{file}", "{{install_path}}/license.txt"]'
        cmd = cmd.format(file=self.license_path)
        return '\n'.join((comment, cmd))


def _get_binaries_url(version):
    """Return URL for FreeSurfer `version`."""
    from urllib.parse import urljoin

    from distutils.version import StrictVersion

    base = "https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/{ver}/"

    if version == 'dev':
        rel_url = "freesurfer-Linux-centos6_x86_64-{ver}.tar.gz"
        return urljoin(base, rel_url).format(ver=version)

    version = StrictVersion(version)

    if version >= StrictVersion('6.0.0'):
        rel_url = "freesurfer-Linux-centos6_x86_64-stable-pub-v{ver}.tar.gz"
    elif version >= StrictVersion('5.0.0'):
        rel_url = "freesurfer-Linux-centos4_x86_64-stable-pub-v{ver}.tar.gz"
    elif version >= StrictVersion('3.0.4'):
        rel_url = ("freesurfer-Linux-centos4_x86_64-stable-pub-v{ver}-full"
                   ".tar.gz")
    elif version == StrictVersion('3.0.3'):
        rel_url = "freesurfer-Linux-rh7.3-stable-pub-v{ver}-full.tar.gz"
    elif version == StrictVersion('2.2'):
        rel_url = "freesurfer-Linux-centos4.0_x86_64-v{ver}.tar.gz"
    else:
        err = "unknown version: {}".format(version)
        raise ValueError(err)

    return urljoin(base, rel_url).format(ver=version)
