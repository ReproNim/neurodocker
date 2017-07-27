"""Class to add FSL installation to Dockerfile.

FSL wiki: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
FSL license: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence
"""
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
        If true, use binaries from FSL's website (default true).
    use_installer : bool
        If true, install FSL using FSL's Python installer. Only works on
        CentOS/RHEL (default false).
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.

    Notes
    -----
    Look into ReproNim/simple_workflow to learn how to install specific versions
    of FSL on Debian (https://github.com/ReproNim/simple_workflow).
    """
    def __init__(self, version, pkg_manager, use_binaries=True,
                 use_installer=False, check_urls=True):
        self.version = LooseVersion(version)
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.use_installer = use_installer
        self.check_urls = check_urls

        self._check_args()
        self.cmd = self._create_cmd()

    def _check_args(self):
        """Raise `ValueError` if combinations of arguments are invalid."""
        if not self.use_binaries + self.use_installer:
            raise ValueError("Please specify installation method.")
        if self.use_binaries and self.use_installer:
            raise ValueError("More than one installation method specified.")
        if self.use_installer and self.pkg_manager != 'yum':
            raise ValueError("FSL's Python installer works only on "
                             "CentOS/RHEL-based systems.")
        return True

    def _create_cmd(self):
        """Return full Dockerfile instructions to install FSL."""
        comment = ("#-----------------------------------------------"
                   "\n# Install FSL {}"
                   "\n# Please review FSL's license:"
                   "\n# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence"
                   "\n#-----------------------------------------------"
                   "".format(self.version))
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
        CentOS/RHEL.
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
        """Return URL to binaries for requested version."""
        base = "https://fsl.fmrib.ox.ac.uk/fsldownloads/"
        if self.version >= LooseVersion('5.0.9'):
            url = urljoin(base, "fsl-{ver}-centos6_64.tar.gz")
        else:
            url = urljoin(base, "oldversions/fsl-{ver}-centos5_64.tar.gz")
        url = url.format(ver=self.version)
        if self.check_urls:
            check_url(url)
        return url

    def install_binaries(self, url):
        """Return Dockerfile instructions to install FSL using binaries hosted
        on FSL's website.
        """
        cmd = ('echo "Downloading FSL ..."'
               '\n&& curl -sSL {}'
               '\n| tar zx -C /opt'.format(url))

        if self.version >= LooseVersion('5.0.10'):
            fsl_python = "/opt/fsl/etc/fslconf/fslpython_install.sh"
            cmd +=  "\n&& /bin/bash {} -q -f /opt/fsl".format(fsl_python)

        entrypoint = "/opt/fsl/neurodocker_fsl_startup.sh"
        cmd += ("\n&& entrypoint={}"
                "\n&& echo '#!/usr/bin/env bash' > $entrypoint"
                "\n&& echo 'set +x' > $entrypoint"
                "\n&& echo 'source ${{FSLDIR}}/etc/fslconf/fsl.sh' >> $entrypoint"
                "\n&& echo '$*' >> $entrypoint"
                "\n&& chmod 755 $entrypoint").format(entrypoint)
        cmd = indent("RUN", cmd)

        env_cmd = ("FSLDIR=/opt/fsl"
                   "\nPATH=/opt/fsl/bin:$PATH")
        env_cmd = indent("ENV", env_cmd)

        entrypoint_cmd = 'ENTRYPOINT ["/bin/bash", "{}"]'.format(entrypoint)

        return "\n".join((cmd, env_cmd, entrypoint_cmd))
