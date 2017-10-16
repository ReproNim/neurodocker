"""Add Dockerfile instructions to install Convert3D (C3D).

Project repository: https://sourceforge.net/projects/c3d/


"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

import posixpath

from neurodocker.utils import check_url, indent


class Convert3D(object):
    """Add Dockerfile instructions to install Convert3D (C3D).

    Copied from Dockerfile at
    https://github.com/nipy/nipype/blob/master/docker/base.Dockerfile#L110-L116

    Parameters
    ----------
    version : str
        C3D version.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.
    """
    VERSION_TARBALLS = {"nightly": "https://sourceforge.net/projects/c3d/files/c3d/Nightly/c3d-nightly-Linux-x86_64.tar.gz/download",
                        "1.0.0": "https://sourceforge.net/projects/c3d/files/c3d/1.0.0/c3d-1.0.0-Linux-x86_64.tar.gz/download",}

    def __init__(self, version, pkg_manager, check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install Convert3D."""
        comment = ("#------------------------"
                   "\n# Install Convert3D {}"
                   "\n#------------------------".format(self.version))

        chunks = [comment, self.install_binaries()]
        return "\n".join(chunks)

    def install_binaries(self):
        """Return command to download and install C3D binaries."""
        try:
            url = Convert3D.VERSION_TARBALLS[self.version.lower()]
        except KeyError:
            raise ValueError("Unsupported version: {}".format(self.version))

        if self.check_urls:
            check_url(url)

        cmd = ('echo "Downloading C3D ..."'
               "\n&& mkdir /opt/c3d"
               "\n&& curl -sSL --retry 5 {}"
               "\n| tar -xzC /opt/c3d --strip-components=1".format(url))
        cmd = indent("RUN", cmd)

        c3d_path = "/opt/c3d"
        c3d_bin_path = posixpath.join(c3d_path, 'bin')
        env_cmd = ("C3DPATH={}"
                   "\nPATH={}:$PATH").format(c3d_path, c3d_bin_path)
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((cmd, env_cmd))
