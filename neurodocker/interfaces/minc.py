"""Add Dockerfile instructions to install MINC.

Homepage: http://www.bic.mni.mcgill.ca/ServicesSoftware/MINC
GitHub repo: https://github.com/BIC-MNI/minc-toolkit-v2
Documentation: https://en.wikibooks.org/wiki/MINC
Installation: https://bic-mni.github.io/

Notes
-----
- Latest releases are from https://bic-mni.github.io/
"""
# Author: Sulantha Mathotaarachchi <sulantha.s@gmail.com>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs

class MINC(object):
    """Add Dockerfile instructions to install MINC.

        Parameters
        ----------
        version : str
            MINC release version. Must be version string.
        pkg_manager : {'apt', 'yum'}
            Linux package manager.
        use_binaries : bool
        If true, uses pre-compiled MINC binaries. True by default.
        check_urls : bool
            If true, raise error if a URL used by this class responds with an error
            code.
    """

    VERSION_Releases = {
        "1.9.15": "http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.15-20170529-Ubuntu_16.04-x86_64.deb",
    }
    BEAST_URL = {
        'latest': "http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/beast-library-1.1.0-20121212.deb"
    }
    MODELS_URL = {
        'latest': "http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/bic-mni-models-0.1.1-20120421.deb"
    }

    def __init__(self, version, pkg_manager, use_binaries=True, check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install MINC."""
        comment = ("#--------------------\n"
                   "# Install MINC {}\n"
                   "#--------------------".format(self.version))

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            raise ValueError("`use_binaries=True` is the only available "
                             "option at this time.")

        return "\n".join(chunks)

    def _get_binaries_urls(cls, version):
        try:
            return MINC.VERSION_Releases[version]
        except KeyError:
            raise ValueError("MINC version not available: {}".format(version))

    def _get_binaries_dependencies(self):
        base_deps = {
            'apt': 'libc6 libstdc++6 imagemagick perl',
            'yum': 'glibc libstdc++ ImageMagick perl',
        }
        return base_deps[self.pkg_manager]

    def _install_binaries_deps(self):
        """Install the dependencies for binary installation
        """
        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        return cmd.format(pkgs=self._get_binaries_dependencies())

    def install_binaries(self):
        """Return Dockerfile instructions to download and install MINC
        binaries.
        """
        from neurodocker.dockerfile import _add_to_entrypoint
        minc_url = self._get_binaries_urls(self.version)
        beast_url = self.BEAST_URL['latest']
        models_url = self.MODELS_URL['latest']
        if self.check_urls:
            check_url(minc_url)
            check_url(beast_url)
            check_url(models_url)

        deps_cmd = self._install_binaries_deps()
        deps_cmd = indent("RUN", deps_cmd)

        ent = _add_to_entrypoint("source /opt/minc/{}/minc-toolkit-config.sh".format(self.version),
                                 with_run=False)

        cmd = ('echo "Downloading MINC, BEASTLIB, and MODELS..."'
               "\n&& curl --retry 5 -o /tmp/minc.deb -sSL {minc_url}"
               "\n&& dpkg -i /tmp/minc.deb && rm -f /tmp/minc.deb"
               "\n&& curl --retry 5 -o /tmp/beast.deb -sSL {beast_url}"
               "\n&& dpkg -i /tmp/beast.deb && rm -f /tmp/beast.deb"
               "\n&& curl --retry 5 -o /tmp/models.deb -sSL {models_url}"
               "\n&& dpkg -i /tmp/models.deb && rm -f /tmp/models.deb"
               "\n&& {entrypoint_cmd}".format(minc_url=minc_url, beast_url=beast_url, models_url=models_url,
                                              entrypoint_cmd=ent))
        cmd = indent("RUN", cmd)

        return "\n".join((deps_cmd, cmd))
