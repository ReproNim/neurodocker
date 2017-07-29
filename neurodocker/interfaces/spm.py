"""Add Dockerfile instructions to install SPM.

Project website: http://www.fil.ion.ucl.ac.uk/spm/

This script installs the standalone SPM, which requires MATLAB Compiler Runtime
but does not require a MATLAB license.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
from distutils.version import LooseVersion
import logging

try:
    from urllib.parse import urljoin  # Python 3
except ImportError:
    from urlparse import urljoin  # Python 2

from neurodocker.utils import check_url, indent, manage_pkgs

logger = logging.getLogger(__name__)


class SPM(object):
    """Add Dockerfile instructions to install SPM. For now, only SPM12 and
    MATLAB R2017a are supported.

    Inspired by the Dockerfile at https://hub.docker.com/r/nipype/workshops/
    `docker pull nipype/workshops:latest-complete`

    Parameters
    ----------
    version : {12}
        SPM version.
    matlab_version : str
        MATLAB version. For example, 'R2017a'.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.

    Notes
    -----
    Instructions to install MATLAB Compiler Runtime can be found at
    https://www.mathworks.com/help/compiler/install-the-matlab-runtime.html.
    """
    def __init__(self, version, matlab_version, pkg_manager, check_urls=True):
        self.version = str(version)
        self.matlab_version = LooseVersion(matlab_version)
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls

        if self.version not in ['12']:
            raise ValueError("Only SPM12 is supported (for now).")

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install MCR and standalone SPM."""
        comment = ("#----------------------\n"
                   "# Install MCR and SPM{}\n"
                   "#----------------------".format(self.version))
        chunks = [comment, self.install_mcr(), '', self.install_spm()]
        return "\n".join(chunks)

    def _install_libs(self):
        """Return Dockerfile instructions to install libxext6 and libxt6.
        Without these libraries, SPM encounters segmentation fault."""
        libs = {'apt': 'libxext6 libxt6',
                'yum': 'libXext.x86_64 libXt.x86_64'}
        cmd = ("{install}"
               "\n&& {clean}").format(**manage_pkgs[self.pkg_manager])
        return cmd.format(pkgs=libs[self.pkg_manager])

    def _get_mcr_url(self):
        base = 'https://www.mathworks.com/supportfiles/'
        if self.matlab_version > LooseVersion("R2013a"):
            rel = ('downloads/{ver}/deployment_files/{ver}/installers/'
                   'glnxa64/MCR_{ver}_glnxa64_installer.zip')
        else:
            rel = ('MCR_Runtime/{ver}/MCR_{ver}_glnxa64_installer.zip')
        url = urljoin(base, rel).format(ver=self.matlab_version)
        if self.check_urls:
            check_url(url)
        return url

    def install_mcr(self):
        """Return Dockerfile instructions to install MATLAB Compiler Runtime."""
        url = self._get_mcr_url()
        comment = "# Install MATLAB Compiler Runtime"
        cmd = self._install_libs()
        cmd += ("\n# Install MATLAB Compiler Runtime"
               '\n&& echo "Downloading MATLAB Compiler Runtime ..."'
               "\n&& curl -sSL -o /tmp/mcr.zip {}"
               "\n&& unzip -q /tmp/mcr.zip -d /tmp/mcrtmp"
               "\n&& /tmp/mcrtmp/install -destinationFolder /opt/mcr -mode silent -agreeToLicense yes"
               "\n&& rm -rf /tmp/*".format(url))
        cmd = indent("RUN", cmd)
        return '\n'.join((comment, cmd))

    def _get_spm_url(self):
        url = ("http://www.fil.ion.ucl.ac.uk/spm/download/restricted/"
               "utopia/dev/spm{spm}_latest_Linux_{matlab}.zip"
               "".format(spm=self.version, matlab=self.matlab_version))
        if self.check_urls:
            check_url(url)
        return url

    def install_spm(self):
        """Return Dockerfile instructions to install standalone SPM."""
        url = self._get_spm_url()
        comment = "# Install standalone SPM"
        cmd = ('echo "Downloading standalone SPM ..."'
               "\n&& curl -sSL -o spm.zip {}"
               "\n&& unzip -q spm.zip -d /opt"
               "\n&& rm -rf spm.zip\n".format(url))
        cmd = indent("RUN", cmd)

        env_cmd = ("MATLABCMD=/opt/mcr/v*/toolbox/matlab"
                   '\nSPMMCRCMD="/opt/spm*/run_spm*.sh /opt/mcr/v*/ script"'
                   "\nFORCE_SPMMCR=1"
                   "\nLD_LIBRARY_PATH=/opt/mcr/v*/runtime/glnxa64:/opt/mcr/v*/bin/glnxa64:/opt/mcr/v*/sys/os/glnxa64:$LD_LIBRARY_PATH")
        env_cmd = indent("ENV", env_cmd)
        return '\n'.join((comment, cmd, env_cmd))
