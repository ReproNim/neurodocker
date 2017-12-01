"""Add Dockerfile instructions to install dcm2niix.

Project repository: https://github.com/rordenlab/dcm2niix
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs


class Dcm2niix(object):
    """Add Dockerfile instructions to install dcm2niix.

    Parameters
    ----------
    version : str
        Dcm2niix version. Use "latest" or "master" for version of current
        master branch. Can also be git commit hash or git tag.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.
    """

    def __init__(self, version, pkg_manager, check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls

        if self.version in ["latest", "master"]:
            self.version = "master"

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install ANTs."""
        comment = ("#------------------------\n"
                   "# Install dcm2niix {}\n"
                   "#------------------------".format(self.version))
        chunks = [comment, self.build_from_source()]
        return "\n".join(chunks)

    def build_from_source(self):
        """Return Dockerfile instructions to build dcm2niix from source.
        """
        pkgs = {'apt': 'cmake g++ gcc git make pigz zlib1g-dev',
                'yum': 'cmake gcc-c++ git libstdc++-static make pigz zlib-devel'}

        url = ("https://github.com/rordenlab/dcm2niix/tarball/{}"
               .format(self.version))
        if self.check_urls:
            check_url(url)

        workdir_cmd = "WORKDIR /tmp"
        cmd = ("deps='{pkgs}'"
               "\n&& {install}"
               "\n&& {clean}"
               "\n&& mkdir dcm2niix"
               "\n&& curl -sSL {url} | tar xz -C dcm2niix --strip-components 1"
               "\n&& mkdir dcm2niix/build && cd dcm2niix/build"
               "\n&& cmake .. && make"
               "\n&& make install"
               "\n&& rm -rf /tmp/*"
               "".format(pkgs=pkgs[self.pkg_manager], url=url,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs='$deps')
        cmd = indent("RUN", cmd)

        return "\n".join((workdir_cmd, cmd))
