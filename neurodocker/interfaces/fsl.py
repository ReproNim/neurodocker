"""Class to add FSL installation to Dockerfile."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
import logging

from neurodocker.utils import add_neurodebian, check_url, indent, manage_pkgs

logger = logging.getLogger(__name__)


class FSL(object):
    """Add Dockerfile instructions to install FSL.

    Parameters
    ----------
    version : str
        Version of FSL. Latest version is installed if using the Python
        installer.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool
        If true, use binaries from FSL's website (compiled on Centos 5).
        Defaults to True.
    use_installer : bool
        If true, install with the latest version of FSL using FSL's Python
        installer. Only works on CentOS/RHEL.
    use_neurodebian : bool
        If true, install FSL from NeuroDebian. Only latest version is supported
        (for now).
    os_codename : str
        Operating system codename (e.g., 'zesty', 'jessie'.) Only required if
        `pkg_manager` is 'apt'. Corresponds to the NeuroDebian url:
        http://neuro.debian.net/lists/OS_CODENAME.us-nh.full.

    Notes
    -----
    Look into ReproNim/simple_workflow to learn how to install specific versions
    of FSL on Debian (https://github.com/ReproNim/simple_workflow).
    """
    def __init__(self, version, pkg_manager, use_binaries=False,
                 use_installer=False, use_neurodebian=False, os_codename=None,
                 check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.use_installer = use_installer
        self.use_neurodebian = use_neurodebian
        self.os_codename = os_codename
        self.check_urls = check_urls

        self._check_args()
        self.cmd = self._create_cmd()

    def _check_args(self):
        """Raise `ValueError` if combinations of arguments are invalid."""
        if self.use_binaries + self.use_installer + self.use_neurodebian > 1:
            raise ValueError("More than one installation method specified.")
        if self.use_installer and self.pkg_manager != 'yum':
            raise ValueError("FSL's Python installer does not work on "
                             "Debian-based systems.")
        if self.use_neurodebian and self.pkg_manager != 'apt':
            raise ValueError("NeuroDebian is an apt repository. It cannot be "
                             "used with other package manageres.")
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
            cmd = self.install_binaries()
        elif self.use_installer:
            cmd = self.install_with_pyinstaller()
        elif self.use_neurodebian:
            cmd = self.install_5_0_8_apt()
        else:
            raise ValueError("Please specify installation method.")

        return "\n".join((comment, cmd))

    def install_5_0_8_apt(self):
        """Return Dockerfile instructions to install FSL 5.0.8 from NeuroDebian.
        """
        if self.version != "5.0.8":
            raise ValueError("Installation by NeuroDebain only supports "
                             "version 5.0.8 supported for now.")
        comments = ["# Add NeuroDebian repository",
                    "# Install FSL",]
        neuro_cmd = add_neurodebian(self.os_codename,
                                    check_urls=self.check_urls)

        cmd = ("deps='fsl-5.0-core fsl-mni152-templates fsl-atlases "
               "fsl-5.0-eddy-nonfree octave'\n"
               "&& {install}\n"
               "&& {clean}".format(**manage_pkgs['apt']))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)

        env_cmd = ("FSLDIR=/usr/share/fsl/5.0\n"
                   "FSLOUTPUTTYPE=NIFTI_GZ\n"
                   "FSLMULTIFILEQUIT=TRUE\n"
                   "POSSUMDIR=/usr/share/fsl/5.0\n"
                   "LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH\n"
                   "FSLTCLSH=/usr/bin/tclsh\n"
                   "FSLWISH=/usr/bin/wish\n"
                   "PATH=/usr/lib/fsl/5.0:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((comments[0], neuro_cmd, comments[1], cmd, env_cmd))

    def install_with_pyinstaller(self):
        """Return Dockerfile instructions to install FSL using FSL's Python
        installer. This will install the latest version and only works on
        Centos/RHEL.
        """
        # TODO: installer script can take a tarball. Try installing previous
        # version using that method.
        workdir_cmd = "WORKDIR /opt"
        env_cmd = "ENV SHELL='bash'"

        url = "https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py"
        if self.check_urls:
            check_url(url)
        cmd = ("deps='bzip2 wget'\n"
               "&& {install}\n"
               "&& wget -q {url}\n"
               "&& python fslinstaller.py --dest=/opt --quiet\n"
               "&& cp /opt/fsl/etc/fslconf/fsl.sh /etc/profile.d/\n"
               "&& rm -f fslinstaller.py\n"
               "&& {remove}\n"
               "&& {clean}\n"
               "".format(url=url, **manage_pkgs['yum']))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)
        path_cmd = "ENV PATH=/opt/fsl/bin:$PATH"

        return "\n".join((workdir_cmd, env_cmd, cmd, path_cmd))

    def install_binaries(self):
        """Return Dockerfile instructions to install FSL using binaries hosted
        on FSL's website."""
        # URL pattern:
        # base: https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions/
        # base/fsl-<VERSION>-centos5_64.tar.gz
        workdir_cmd = "WORKDIR /opt"
        env_cmd = "ENV SHELL='bash'"

        base_url = "https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions"
        tarball = "fsl-{}-centos5_64.tar.gz".format(self.version)
        url = "{}/{}".format(base_url, tarball)
        if self.check_urls:
            check_url(url)

        cmd = ("deps='ca-certificates bzip2 wget'\n"
               "&& {install}\n"
               "&& wget -qO- {url} | tar xvz\n"
               # "&& rm -f {tarball}\n"
               "&& cp fsl/etc/fslconf/fsl.sh /etc/profile.d/\n"
               "&& {remove}\n"
               "&& {clean}"
               "".format(url=url, tarball=tarball,
                         **manage_pkgs[self.pkg_manager]))
        cmd = cmd.format(pkgs="$deps")
        cmd = indent("RUN", cmd)
        fsl_env_cmd = ("ENV FSLDIR=/opt/fsl\n"
                       "ENV PATH=$FSLDIR/bin:$PATH")


        return "\n".join((workdir_cmd, env_cmd, cmd, fsl_env_cmd))
