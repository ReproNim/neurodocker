"""Add Dockerfile instructions to add NeuroDebian repository."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from neurodocker.utils import check_url, indent, manage_pkgs


class NeuroDebian(object):
    """Object to add NeuroDebian repository.

    Parameters
    ----------
    os_codename : str
        Operating system codename (e.g., 'zesty', 'jessie').
    download_server : {'australia', 'china-tsinghua', 'china-scitech',
                       'china-zhejiang', 'germany-munich', 'germany-magdeburg',
                       'greece', 'japan', 'usa-ca', 'usa-nh', 'usa-tn'}
        The server to use to download NeuroDebian packages. Choose the one
        closest to you.
    full : bool
        If false (default), use the libre sources. If true, use the full
        NeuroDebian sources.
    pkgs : str or list or tuple
        Packages to install from NeuroDebian.
    pkg_manager : {'apt'}
        Linux package manager.
    check_urls : bool
        If true, raise error if URLs used by this class return an error code.
    """

    SERVERS = {'australia': 'au',
               'china-tsinghua': 'cn-bj1',
               'china-scitech': 'cn-bj2',
               'china-zhejiang': 'cn-zj',
               'germany-munich': 'de-m',
               'germany-magdeburg': 'de-md',
               'greece': 'gr',
               'japan': 'jp',
               'usa-ca': 'us-ca',
               'usa-nh': 'us-nh',
               'usa-tn': 'us-tn',}

    def __init__(self, os_codename, download_server, full=False, pkgs=None,
                 pkg_manager='apt', check_urls=True):
        self.pkgs = pkgs
        self.check_urls = check_urls

        download_server = self._get_server(download_server)
        suffix = "full" if full else "libre"
        self.url = self._create_url(os_codename, download_server, suffix)
        if self.check_urls:
            check_url(self.url)

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        comment = ("#---------------------------"
                   "\n# Add NeuroDebian repository"
                   "\n#---------------------------")

        chunks = [comment, self._add_neurodebian()]
        if self.pkgs is not None and self.pkgs:
            chunks.append(self._install_pkgs())
        return "\n".join(chunks)

    @classmethod
    def _get_server(cls, download_server):
        try:
            return cls.SERVERS[download_server]
        except KeyError:
            raise ValueError("Invalid download server: {}"
                             "".format(download_server))

    @staticmethod
    def _create_url(os_codename, download_server, suffix):
        """Return neurodebian URL."""
        try:
            from urllib.parse import urljoin  # Python 3
        except ImportError:
            from urlparse import urljoin  # Python 2

        base = "http://neuro.debian.net/lists/"
        rel = "{0}.{1}.{2}".format(os_codename, download_server, suffix)
        return urljoin(base, rel)

    def _add_neurodebian(self):
        """Return instruction to add NeuroDebian repository."""
        pkgs = "dirmngr"
        cmd = ("{install}"
               "\n&& {clean}"
               "\n&& curl -sSL {url}"
               "\n> /etc/apt/sources.list.d/neurodebian.sources.list"
               "\n&& apt-key adv --recv-keys --keyserver"
               " hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9"
               "\n&& apt-get update"
               "\n&& {remove}"
               "".format(url=self.url, **manage_pkgs['apt']).format(pkgs=pkgs))
        return indent("RUN", cmd)

    def _install_pkgs(self):
        """Return instruction to install NeuroDebian packages."""
        if isinstance(self.pkgs, (list, tuple)):
            self.pkgs = " ".join(self.pkgs)

        cmd = ("{install}\n&& {clean}".format(**manage_pkgs['apt'])
               .format(pkgs=self.pkgs))
        comment = "\n# Install NeuroDebian packages"
        return "\n".join((comment, indent("RUN", cmd)))
