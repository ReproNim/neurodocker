"""Add Dockerfile instructions to install ANTs.

Project repository: https://github.com/stnava/ANTs/

ANTs recommends building from source. Versions 2.0.0 and newer are available
on GitHub, and older versions are available on SourceForge.

Build from source (takes approximately 40 minutes):
https://github.com/stnava/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS
"""
from __future__ import absolute_import, division, print_function

from src.docker.utils import indent
from src.utils import logger

manage_pkgs = {'apt': {'install': ('apt-get update -qq && apt-get install -yq '
                                   '--no-install-recommends {pkgs}'),
                       'remove': 'apt-get purge -y --auto-remove {pkgs}'},
               'yum': {'install': 'yum install -y -q {pkgs}',
                       # Trying to uninstall ca-certificates breaks things.
                       'remove': 'yum remove $(echo "{pkgs}" | sed "s/ca-certificates//g")'},}


class ANTs(object):
    """Add Dockerfile instructions to install ANTs. Versions 2.x are
    supported.

    Inspired by the Dockerfile at https://hub.docker.com/r/nipype/workshops/
    `docker pull nipype/workshops:latest-nofsspm`

    Parameters
    ----------
    version : str
        ANTs version.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool
        If true, uses pre-compiled ANTs binaries. If false, attempts to build
        from source.
    """
    VERSION_HASHES = {"latest": None,
                      "2.1.0": "78931aa6c4943af25e0ee0644ac611d27127a01e",
                      "2.1.0rc3": "465cc8cdf0f8cc958edd2d298e05cc2d7f8a48d8",
                      "2.1.0rc2": "17160f72f5e1c9d6759dd32b7f2dc0b36ded338b",
                      "2.1.0rc1": "1593a7777d0e6c8be0b9462012328bde421510b9",
                      "2.0.3": "c9965390c1a302dfa9e63f6ca3cb88f68aab329f",
                      "2.0.2": "7b83036c987e481b2a04490b1554196cb2fc0dab",
                      "2.0.1": "dd23c394df9292bae4c5a4ece3023a7571791b7d",
                      "2.0.0": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",
                      "HoneyPot": "7ae1107c102f7c6bcffa4df0355b90c323fcde92",}

    VERSION_TARBALLS = {"2.1.0": "https://www.dropbox.com/s/x7eyk125bhwiisu/ants-2.1.0_centos-5.tar.gz?dl=1",
                        "2.0.3": "https://www.dropbox.com/s/09yd0jbohcwl24z/ants-2.0.3_centos-5.tar.gz?dl=1",}

    def __init__(self, version, pkg_manager, use_binaries=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries

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
        try:
            url = ANTs.VERSION_TARBALLS[self.version]
        except KeyError:
            raise ValueError("No tarball for version {}".format(self.version))

        workdir_cmd = "WORKDIR /opt"
        cmd = ("deps='ca-certificates wget'\n"
               "&& {install}\n"
               "&& wget -qO ants.tar.gz {url}\n"
               "&& tar xzf ants.tar.gz\n"
               "&& rm -f ants.tar.gz\n"
               "&& {remove}"
               "".format(url=url, **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)
        # Requires two ENV instructions because the second uses one defined in
        # the first.
        env_cmd = ("ENV ANTSPATH=/opt/ants\n"
                    "ENV PATH=$ANTSPATH:$PATH")
        return "\n".join((workdir_cmd, cmd, env_cmd))

    def build_from_source_github(self):
        """Return Dockerfile instructions to build ANTs from source."""
        pkgs = {'apt': 'ca-certificates cmake g++ gcc git make zlib1g-dev',
                'yum': 'ca-certificates cmake gcc-c++ git make zlib-devel'}

        if self.version == "latest":
            checkout = ""
        else:
            version_hash = ANTs.VERSION_HASHES[self.version]
            checkout = "&& git checkout {}\n".format(version_hash)

        workdir_cmd = "WORKDIR /tmp/ants-build"
        cmd = ("deps='{pkgs}'\n"
               "&& {install}\n"
               "&& git clone https://github.com/stnava/ANTs.git\n"
               "&& cd ANTs\n"
               "{checkout}"
               "&& cd .. && mkdir build && cd build\n"
               "&& cmake ../ANTs && make -j 2\n"
               "&& mkdir -p /opt/ants\n"
               "&& mv bin/* /opt/ants && mv ../ANTs/Scripts/* /opt/ants\n"
               "&& cd /tmp && rm -rf ants-build\n"
               "&& {remove}"
               "".format(pkgs=pkgs[self.pkg_manager], checkout=checkout,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs='$deps')
        cmd = indent("RUN", cmd)

        env_cmd = ("ENV ANTSPATH=/opt/ants\n"
                   "ENV PATH=$ANTSPATH:$PATH")

        return "\n".join((workdir_cmd, cmd, env_cmd))
