"""Add Dockerfile instructions to install ANTs.

Project repository: https://github.com/stnava/ANTs/

ANTs recommends building from source. Jakub Kaczmarzyk build several versions
on CentOS 6 Docker images. Those Docker images are located at
https://hub.docker.com/r/kaczmarj/ants/ and the binaries are on Dropbox. See
the ANTs class definition for the Dropbox URLs.

Source for ANTs versions 2.0.0 and newer are available on GitHub, and older
versions are available on SourceForge.

Instructions to build from source (takes approximately 40 minutes):
https://github.com/stnava/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs


class ANTs(object):
    """Add Dockerfile instructions to install ANTs. Versions 2.0.0 and newer
    are supported. Pre-compiled binaries can be downloaded, or ANTs can be
    built from source. The pre-compiled binaries were compiled on a CentOS 6
    Docker image. The build log file is present in the ANTs tarball.

    Inspired by the Dockerfile at https://hub.docker.com/r/nipype/workshops/
    `docker pull nipype/workshops:latest-nofsspm`

    Parameters
    ----------
    version : str
        ANTs version.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool, str
        If true, uses pre-compiled ANTs binaries. If false, attempts to build
        from source.
    git_hash : str
        If this is specified and use_binaries is false, build from source from
        this commit. If this is not specified and use_binaries is false, will
        use git hash of the specified version.
    check_urls : bool
        If true, raise error if a URL used by this class responds with a status
        code greater than 400.
    """
    VERSION_HASHES = {"latest": None,
                      "2.2.0": "0740f9111e5a9cd4768323dc5dfaa7c29481f9ef",
                      "2.1.0": "78931aa6c4943af25e0ee0644ac611d27127a01e",
                      "2.1.0rc3": "465cc8cdf0f8cc958edd2d298e05cc2d7f8a48d8",
                      "2.1.0rc2": "17160f72f5e1c9d6759dd32b7f2dc0b36ded338b",
                      "2.1.0rc1": "1593a7777d0e6c8be0b9462012328bde421510b9",
                      "2.0.3": "c9965390c1a302dfa9e63f6ca3cb88f68aab329f",
                      "2.0.2": "7b83036c987e481b2a04490b1554196cb2fc0dab",
                      "2.0.1": "dd23c394df9292bae4c5a4ece3023a7571791b7d",
                      "2.0.0": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",
                      "HoneyPot": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",}

    VERSION_TARBALLS = {"2.2.0": "https://dl.dropbox.com/s/2f4sui1z6lcgyek/ANTs-Linux-centos5_x86_64-v2.2.0-0740f91.tar.gz",
                        "2.1.0": "https://dl.dropbox.com/s/h8k4v6d1xrv0wbe/ANTs-Linux-centos5_x86_64-v2.1.0-78931aa.tar.gz",
                        "2.0.3": "https://dl.dropbox.com/s/oe4v52lveyt1ry9/ANTs-Linux-centos5_x86_64-v2.0.3-c996539.tar.gz",
                        "2.0.0": "https://dl.dropbox.com/s/kgqydc44cc2uigb/ANTs-Linux-centos5_x86_64-v2.0.0-7ae1107.tar.gz",}

    def __init__(self, version, pkg_manager, use_binaries=True, git_hash=None,
                 check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.git_hash = git_hash
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install ANTs."""
        comment = ("#-------------------\n"
                   "# Install ANTs {}\n"
                   "#-------------------".format(self.version))

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            chunks = [comment, self.build_from_source_github()]

        return "\n".join(chunks)

    def install_binaries(self):
        """Return command to download and install ANTs binaries. Supports
        custom URL with tarball of binaries.
        """
        try:
            url = ANTs.VERSION_TARBALLS[self.version]
        except KeyError:
            raise ValueError("Tarball not available for version {}."
                             "".format(self.version))

        if self.check_urls:
            check_url(url)

        cmd = ("RUN curl -sSL --retry 5 {} | tar zx -C /opt".format(url))

        env_cmd = ("ANTSPATH=/opt/ants"
                   "\nPATH=/opt/ants:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((cmd, env_cmd))

    def build_from_source_github(self):
        """Return Dockerfile instructions to build ANTs from source. Checkout
        to commit based on git_hash or version. If 'latest', build from master.
        """
        pkgs = {'apt': 'cmake g++ gcc git make zlib1g-dev',
                'yum': 'cmake gcc-c++ git make zlib-devel'}

        if self.git_hash is None:
            try:
                self.git_hash = ANTs.VERSION_HASHES[self.version]
            except KeyError:
                raise ValueError("git hash not known for version {}"
                                 "".format(self.version))

        if self.version == "latest":
            checkout = ""
        else:
            checkout = ("\n&& cd ANTs"
                        "\n&& git checkout {}"
                        "\n&& cd .."
                        "".format(self.git_hash))

        workdir_cmd = "WORKDIR /tmp/ants-build"
        cmd = ("deps='{pkgs}'"
               "\n&& {install}"
               "\n&& {clean}"
               "\n&& git clone https://github.com/stnava/ANTs.git"
               "{checkout}"
               "\n&& mkdir build && cd build"
               "\n&& cmake ../ANTs && make -j 1"
               "\n&& mkdir -p /opt/ants"
               "\n&& mv bin/* /opt/ants && mv ../ANTs/Scripts/* /opt/ants"
               "\n&& rm -rf /tmp/*"
               "\n&& {remove}"
               "".format(pkgs=pkgs[self.pkg_manager], checkout=checkout,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs='$deps')
        cmd = indent("RUN", cmd)

        env_cmd = ("ANTSPATH=/opt/ants\n"
                   "PATH=/opt/ants:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((workdir_cmd, cmd, env_cmd))
