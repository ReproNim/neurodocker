"""Add Dockerfile instructions to install PETPVC.

Homepage: https://github.com/UCL/PETPVC
GitHub repo: https://github.com/UCL/PETPVC
Documentation: https://github.com/UCL/PETPVC
Installation: https://github.com/UCL/PETPVC

Notes
-----
- Latest releases are from https://github.com/UCL/PETPVC
"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs

class PETPVC(object):
    """Add Dockerfile instructions to install PETPVC.

        Parameters
        ----------
        version : str
            PETPVC release version. Must be version string.
        pkg_manager : {'apt', 'yum'}
            Linux package manager.
        use_binaries : bool
        If true, uses pre-compiled PETPVC binaries. True by default.
        check_urls : bool
            If true, raise error if a URL used by this class responds with an error
            code.
    """

    VERSION_Releases = {
        "1.2.0-b": "https://github.com/UCL/PETPVC/releases/download/v1.2.0-b/PETPVC-1.2.0-b-Linux.tar.gz",
        "1.2.0-a": "https://github.com/UCL/PETPVC/releases/download/v1.2.0-a/PETPVC-1.2.0-a-Linux.tar.gz",
        "1.1.0": "https://github.com/UCL/PETPVC/releases/download/v1.1.0/PETPVC-1.1.0-Linux.tar.gz",
        "1.0.0": "https://github.com/UCL/PETPVC/releases/download/v1.0.0/PETPVC-1.0.0-Linux.tar.gz",
    }

    def __init__(self, version, pkg_manager, use_binaries=True, check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install PETPVC."""
        comment = ("#--------------------\n"
                   "# Install PETPVC {}\n"
                   "#--------------------".format(self.version))

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            raise ValueError("`use_binaries=True` is the only available "
                             "option at this time.")

        return "\n".join(chunks)

    def _get_binaries_urls(self, version):
        try:
            return PETPVC.VERSION_Releases[version]
        except KeyError:
            raise ValueError("PETPVC version not available: {}".format(version))

    def _get_install_cmd(self, petpvc_url):
        cmd = ('echo "Downloading PETPVC..."'
               "\n&& curl --retry 5 -sSL {petpvc_url}"
                "\n| tar xz --strip-components=1 -C /opt/petpvc"
               .format(petpvc_url=petpvc_url))
        return cmd

    def install_binaries(self):
        """Return Dockerfile instructions to download and install PETPVC
        binaries.
        """
        petpvc_url = self._get_binaries_urls(self.version)
        if self.check_urls:
            check_url(petpvc_url)

        cmd = self._get_install_cmd(petpvc_url)
        cmd = indent("RUN", cmd)

        env_cmd = ("ENV PATH=/opt/petpvc/bin:$PATH")

        return "\n".join((cmd, env_cmd))
