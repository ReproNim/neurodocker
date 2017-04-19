"""Add Dockerfile instructions to install SPM.

Project website: http://www.fil.ion.ucl.ac.uk/spm/

This script installs the standalone SPM, which requires MATLAB Compiler Runtime
but does not require a MATLAB license.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
import logging

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
        If true, throw warning if URLs relevant to the installation cannot be
        reached.
    """
    def __init__(self, version, matlab_version, pkg_manager, check_urls=True):
        self.version = str(version)
        self.matlab_version = matlab_version
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls

        if self.version not in ['12'] or self.matlab_version not in ['R2017a']:
            raise ValueError("Only SPM12 and MATLAB R2017a are supported.")

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install MCR and standalone SPM."""
        comment = ("#----------------------\n"
                   "# Install MCR and SPM{}\n"
                   "#----------------------".format(self.version))
        chunks = [comment, self.install_libs(), '', self.install_mcr(), '',
                  self.install_spm()]
        return "\n".join(chunks)

    def install_libs(self):
        """Return Dockerfile instructions to install libxext6 and libxt6.
        Without these libraries, SPM encounters segmentation fault."""
        libs = {'apt': 'libxext6 libxt6',
                'yum': 'libXext.x86_64 libXt.x86_64'}
        comment = "# Install required libraries"
        cmd = "RUN {install}".format(**manage_pkgs[self.pkg_manager])
        cmd = cmd.format(pkgs=libs[self.pkg_manager])
        return "\n".join((comment, cmd))

    def install_mcr(self):
        """Return Dockerfile insructions to install MATLAB Compiler Runtime."""
        comment = "# Install MATLAB Compiler Runtime"
        mcr_url = ("https://www.mathworks.com/supportfiles/downloads/{ver}/"
                   "deployment_files/{ver}/installers/glnxa64/"
                   "MCR_{ver}_glnxa64_installer.zip"
                   "".format(ver=self.matlab_version))
        if self.check_urls:
            check_url(mcr_url)

        workdir_cmd = "WORKDIR /opt"
        cmd = ("deps='ca-certificates unzip wget'\n"
               '&& {install}\n'
               '&& echo "destinationFolder=/opt/mcr" > mcr_options.txt\n'
               '&& echo "agreeToLicense=yes" >> mcr_options.txt\n'
               '&& echo "outputFile=/tmp/matlabinstall_log" >> mcr_options.txt\n'
               '&& echo "mode=silent" >> mcr_options.txt\n'
               '&& mkdir -p matlab_installer\n'
               '&& wget -qO matlab_installer/installer.zip {mcr_url}\n'
               '&& unzip matlab_installer/installer.zip -d matlab_installer/\n'
               '&& matlab_installer/install -inputFile /opt/mcr_options.txt\n'
               '&& rm -rf matlab_installer mcr_options.txt\n'
               ''.format(mcr_url=mcr_url, **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)
        return '\n'.join((comment, workdir_cmd, cmd))

    def install_spm(self):
        """Return Dockerfile instructions to install standalone SPM."""
        comment = "# Install standalone SPM"
        spm_url = ("http://www.fil.ion.ucl.ac.uk/spm/download/restricted/"
                   "utopia/dev/spm{spm}_latest_Linux_{matlab}.zip"
                   "".format(spm=self.version, matlab=self.matlab_version))
        if self.check_urls:
            check_url(spm_url)

        workdir_cmd = "WORKDIR /opt"
        cmd = ("deps='ca-certificates unzip wget'\n"
               '&& wget -qO spm{ver}.zip {spm_url}\n'
               '&& unzip spm{ver}.zip\n'
               '&& rm -rf spm{ver}.zip /tmp/*\n'
               '&& {remove}'
               ''.format(spm_url=spm_url, ver=self.version,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)

        # TODO: older versions of MCR might not have the same directory
        # structure. This works with MCR from MATLAB R2017a.
        env_cmd = ('MATLABCMD="/opt/mcr/v92/toolbox/matlab"\n'
                   'SPMMCRCMD="/opt/spm{ver}/run_spm{ver}.sh /opt/mcr/v92/ script"\n'
                   'FORCE_SPMMCR=1\n'
                   'LD_LIBRARY_PATH=/opt/mcr/v92/runtime/glnxa64:'
                   '/opt/mcr/v92/bin/glnxa64:'
                   '/opt/mcr/v92/sys/os/glnxa64:$LD_LIBRARY_PATH'
                   ''.format(ver=self.version))
        env_cmd = indent("ENV", env_cmd)
        return '\n'.join((comment, workdir_cmd, cmd, env_cmd))
