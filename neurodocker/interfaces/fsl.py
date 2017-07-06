"""Class to add FSL installation to Dockerfile."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from distutils.version import LooseVersion
import logging

try:
    from urllib.parse import urljoin  # Python 3
except ImportError:
    from urlparse import urljoin  # Python 2

from neurodocker.utils import check_url, indent

logger = logging.getLogger(__name__)


class FSL(object):
    """Add Dockerfile instructions to install FSL.

    Parameters
    ----------
    version : str
        Version of FSL.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool
        If true, use binaries from FSL's website. True by default if
        use_installer and use_neurodebian are false.
    use_installer : bool
        If true, install FSL using FSL's Python installer. Only works on
        CentOS/RHEL.
    os_codename : str
        Operating system codename (e.g., 'zesty', 'jessie'.) Only required if
        `pkg_manager` is 'apt'. Corresponds to the NeuroDebian url:
        http://neuro.debian.net/lists/<OS_CODENAME>.us-nh.full.

    Notes
    -----
    Look into ReproNim/simple_workflow to learn how to install specific versions
    of FSL on Debian (https://github.com/ReproNim/simple_workflow).
    """
    def __init__(self, version, pkg_manager, use_binaries=None,
                 use_installer=False, use_neurodebian=False, os_codename=None,
                 check_urls=True):
        self.version = LooseVersion(version)
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.use_installer = use_installer
        self.use_neurodebian = use_neurodebian
        self.os_codename = os_codename
        self.check_urls = check_urls

        if (self.use_binaries is None and not self.use_installer
            and not self.use_neurodebian):
            self.use_binaries = True

        self._check_args()
        self.cmd = self._create_cmd()

    def _check_args(self):
        """Raise `ValueError` if combinations of arguments are invalid."""
        if not self.use_binaries + self.use_installer + self.use_neurodebian:
            raise ValueError("Please specify installation method.")
        if self.use_binaries + self.use_installer + self.use_neurodebian > 1:
            raise ValueError("More than one installation method specified.")
        if self.use_installer and self.pkg_manager != 'yum':
            raise ValueError("FSL's Python installer does not work on "
                             "Debian-based systems.")
        if self.use_neurodebian and self.os_codename is None:
            raise ValueError("`os_codename` must be defined to install FSL "
                             "through NeuroDebian.")
        return True

    def _create_cmd(self):
        """Return full Dockerfile instructions to install FSL."""
        comment = ("#------------------\n"
                   "# Install FSL {}\n"
                   "#------------------".format(self.version))
        if self.use_binaries:
            url = self._get_binaries_url()
            cmd = self.install_binaries(url)
        elif self.use_installer:
            cmd = self.install_with_pyinstaller(self.check_urls)
        return "\n".join((comment, cmd))

    @staticmethod
    def install_with_pyinstaller(check_urls=False):
        """Return Dockerfile instructions to install FSL using FSL's Python
        installer. This will install the latest version and only works on
        Centos/RHEL.
        """
        workdir_cmd = "WORKDIR /opt"
        url = "https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py"
        if check_urls:
            check_url(url)
        cmd = ("curl -sSL -o fslinstaller.py {url}"
               "\n&& python fslinstaller.py --dest=/opt --quiet"
               "\n&& . /opt/fsl/etc/fslconf/fsl.sh"
               "\n&& rm -f fslinstaller.py"
               "".format(url=url))
        cmd = indent("RUN", cmd)

        path_cmd = ("FSLDIR=/opt/fsl"
                    "\n&& PATH=/opt/fsl/bin:$PATH")
        path_cmd = indent("ENV", path_cmd)

        return "\n".join((workdir_cmd, cmd, path_cmd))

    def _get_binaries_url(self):
        base = "https://fsl.fmrib.ox.ac.uk/fsldownloads/"
        if self.version >= LooseVersion('5.0.9'):
            url = urljoin(base, "fsl-{ver}-centos6_64.tar.gz")
        else:
            url = urljoin(base, "oldversions/fsl-{ver}-centos5_64.tar.gz")
        url = url.format(ver=self.version)
        if self.check_urls:
            check_url(url)
        return url

    @staticmethod
    def install_binaries(url):
        """Return Dockerfile instructions to install FSL using binaries hosted
        on FSL's website."""
        cmd = ('curl -sSL {url}'
               '\n| tar zx -C /opt'
               '\n&& . /opt/fsl/etc/fslconf/fsl.sh'
               '\n&& FSLPYFILE=/opt/fsl/etc/fslconf/fslpython_install.sh'
               '\n&& [ -f $FSLPYFILE ] && $FSLPYFILE -f /opt/fsl -q || true'
               ''.format(url=url))
        cmd = indent("RUN", cmd)

        env_cmd = ("FSLDIR=/opt/fsl"
                   "\nPATH=/opt/fsl/bin:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((cmd, env_cmd))
