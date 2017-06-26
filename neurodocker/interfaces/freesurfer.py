"""Add Dockerfile instructions to install FreeSurfer.

Project repository: https://github.com/freesurfer/freesurfer
Project website: https://surfer.nmr.mgh.harvard.edu/
Project wiki: https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferWiki
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs


class FreeSurfer(object):
    """Add Dockerfile instructions to install FreeSurfer. A FreeSurfer license
    is required to run the software.

    See FreeSurfer's download and install instructions:
    https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

    Parameters
    ----------
    version : str
        FreeSurfer version (e.g., '6.0.0'). To install nightly build, use
        version='dev'.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool, str
        If true, uses pre-compiled FreeSurfer binaries. Building from source
        is not yet supported.
    check_urls : bool
        If true, raise error if a URL used by this class responds with a status
        code greater than 400.
    """

    def __init__(self, version, pkg_manager, use_binaries=True,
                 check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install FreeSurfer."""
        comment = ("#--------------------------\n"
                   "# Install FreeSurfer v{}\n"
                   "#--------------------------".format(self.version))

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            raise ValueError("Installation via binaries is the only available "
                             "installation method for now.")

        return "\n".join(chunks)

    def _get_binaries_url(self):
        """Return URL for FreeSurfer `version`."""
        from distutils.version import StrictVersion
        try:
            from urllib.parse import urljoin  # python 3
        except ImportError:
            from urlparse import urljoin  # python 2

        if self.version == 'dev':
            return ("ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/dev/"
                    "freesurfer-Linux-centos6_x86_64-dev.tar.gz")

        version = StrictVersion(self.version)
        base = "https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/{ver}/"

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
            rel_url = ""

        return urljoin(base, rel_url).format(ver=self.version)

    def install_binaries(self):
        """Return command to download and install FreeSurfer binaries."""
        url = self._get_binaries_url()

        if self.check_urls and self.version == 'dev':
            raise ValueError("check_urls=True and version='dev' cannot be used "
                             "together. Set check_urls to False.")
        elif self.check_urls:
            check_url(url)

        env_cmd = "ENV FREESURFER_HOME=/opt/freesurfer"

        cmd = ("curl -sSL --retry 5 {url}"
               "\n| tar xz -C /opt"
               "\n&& . $FREESURFER_HOME/SetUpFreeSurfer.sh".format(url=url))
        cmd = indent("RUN", cmd)

        return "\n".join((env_cmd, cmd))
