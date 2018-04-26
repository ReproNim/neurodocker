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
    VERSION_TARBALLS = {
        "1.9.15": "https://dl.dropbox.com/s/40hjzizaqi91373/minc-toolkit-1.9.15-20170529-CentOS_6.9-x86_64.tar.gz",
    }
    BEAST_URL = {
        "1.1": "http://packages.bic.mni.mcgill.ca/tgz/beast-library-1.1.tar.gz",
    }
    MODELS_URL = {
        "09a": "http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_sym_09a_minc2.zip",
        "09c": "http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/mni_icbm152_nlin_sym_09c_minc2.zip",
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

    def _get_binaries_urls(self, version):
        try:
            return MINC.VERSION_TARBALLS[version]
        except KeyError:
            raise ValueError("MINC version not available: {}".format(version))

    def _get_binaries_dependencies(self):
        pkgs = {
            'apt': 'libgl1-mesa-dev libice6 libsm6 libx11-6 libxext6 libxi6 libxmu6 libgomp1 libjpeg62',
            'yum': 'mesa-libGL-devel libICE libSM libX11 libXext libXi libXmu libgomp libjpeg-turbo',
        }
        return pkgs[self.pkg_manager]

    def _install_binaries_deps(self):
        """Install the dependencies for binary installation
        """
        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        return cmd.format(pkgs=self._get_binaries_dependencies())

    def _get_install_cmd(self, minc_url, beast_url, models_90a_url, models_90c_url, entrypoint_cmd):
        cmd = ('\n&& echo " Downloading MINC, BEASTLIB, and MODELS..."'
               "\n&& curl -sSL --retry 5 {minc_url}"
               "\n| tar zx -C /opt"
               "\n&& curl -sSL --retry 5 {beast_url}"
               "\n| tar zx -C /opt/minc/share"
               "\n&& curl -sSL --retry 5 -o /tmp/mni_90a.zip {models_09a_url}"
               "\n&& unzip /tmp/mni_90a.zip -d /opt/minc/share/icbm152_model_09a"
               "\n&& curl -sSL --retry 5 -o /tmp/mni_90c.zip {models_09c_url}"
               "\n&& unzip /tmp/mni_90c.zip -d /opt/minc/share/icbm152_model_09c"
               "\n&& rm -r /tmp/mni_90* "
               "\n&& {entrypoint_cmd}".format(minc_url=minc_url, beast_url=beast_url, models_09a_url=models_90a_url,
                                              models_09c_url=models_90c_url, entrypoint_cmd=entrypoint_cmd))
        return cmd


    def install_binaries(self):
        """Return Dockerfile instructions to download and install MINC
        binaries.
        """
        from neurodocker.generate import _add_to_entrypoint
        minc_url = self._get_binaries_urls(self.version)
        beast_url = self.BEAST_URL['1.1']
        models_09a_url = self.MODELS_URL['09a']
        models_09c_url = self.MODELS_URL['09c']
        if self.check_urls:
            check_url(minc_url)
            check_url(beast_url)
            check_url(models_09a_url)
            check_url(models_09c_url)

        cmd = self._install_binaries_deps()
        ent = _add_to_entrypoint("source /opt/minc/minc-toolkit-config.sh",
                                 with_run=False)
        cmd += self._get_install_cmd(minc_url, beast_url, models_09a_url, models_09c_url, ent)
        cmd = indent("RUN", cmd)
        return cmd
