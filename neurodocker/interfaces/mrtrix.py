"""Add Dockerfile instructions to install MRtrix.

MRtrix GitHub repository: https://github.com/MRtrix3/mrtrix3

MRtrix recommends building from source. Binaries for MRtrix3 were compiled on
CentOS 6.6 and uploaded to Dropbox. This file uses those binaries if the user
wants to use pre-compiled binaries.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs


class MRtrix3(object):
    """Add Dockerfile instructions to install MRtrix3. Pre-compiled binaries
    can be downloaded, or MRtrix can be built from source. The pre-compiled
    binaries were compiled on a CentOS 6.6 Docker image.

    Parameters
    ----------
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool, str
        If true, uses pre-compiled MRtrix3 binaries. If false, attempts to
        build from source (with -nogui option).
    git_hash : str
        If this is specified and use_binaries is false, checkout to this commit
        before building.
    check_urls : bool
        If true, raise error if a URL used by this class responds with a status
        code greater than 400.
    """

    def __init__(self, pkg_manager, use_binaries=True, git_hash=None,
                 check_urls=True):
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.git_hash = git_hash
        self.check_urls = check_urls

        if not self.use_binaries and self.pkg_manager == "yum":
            raise ValueError("Building MRtrix3 on CentOS/Fedora is not "
                             "supported yet.")

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install MRtrix."""
        comment = ("#----------------\n"
                   "# Install MRtrix3\n"
                   "#----------------")

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            chunks = [comment, self.build_from_source()]

        return "\n".join(chunks)

    def install_binaries(self):
        """Return command to download and install MRtrix3 binaries."""
        url = ("https://www.dropbox.com/s/2g008aaaeht3m45/"
               "mrtrix3-Linux-centos6.tar.gz?dl=0")

        if self.check_urls:
            check_url(url)

        cmd = ('RUN curl -sSL --retry 5 {} | tar zx -C /opt'.format(url))
        env_cmd = ("ENV PATH=/opt/mrtrix3/bin:$PATH")

        return "\n".join((cmd, env_cmd))

    def build_from_source(self):
        """Return Dockerfile instructions to build MRtrix from source. Checkout
        to git_hash if specified.
        """
        # QUESTION: how to download eigen3-devel? Have to add EPEL.
        pkgs = {'apt': 'g++ git libeigen3-dev zlib1g-dev',
                'yum': 'eigen3-devel gcc-c++ git zlib-devel'}

        if self.git_hash == None:
            checkout = ""
        else:
            checkout = ("\n&& git checkout {}".format(self.git_hash))

        workdir_cmd = "WORKDIR /opt"
        cmd = ("deps='{pkgs}'"
               "\n&& {install}"
               "\n&& {clean}"
               "\n&& git clone https://github.com/MRtrix3/mrtrix3.git"
               "\n&& cd mrtrix3"
               "{checkout}"
               "\n&& ./configure -nogui"
               "\n&& ./build"
               "\n&& rm -rf tmp/* /tmp/*"
               "\n&& {remove}"
               "".format(pkgs=pkgs[self.pkg_manager], checkout=checkout,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs='$deps')
        cmd = indent("RUN", cmd)

        env_cmd = ("ENV PATH=/opt/mrtrix3/bin:$PATH")

        return "\n".join((workdir_cmd, cmd, env_cmd))
