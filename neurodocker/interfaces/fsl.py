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

from neurodocker.utils import check_url, indent, manage_pkgs

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
    Look into ReproNim/simple_workflow to learn how to install specific
    versions of FSL on Debian (https://github.com/ReproNim/simple_workflow).
    """
    def __init__(self, version=None, eddy=None, cuda_version=None,
                 pkg_manager=None, use_binaries=True, use_installer=False,
                 check_urls=True):
        self.version = version
        self.eddy = eddy
        self.cuda_version = cuda_version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.use_installer = use_installer
        self.check_urls = check_urls

        if self.version is not None:
            self.version = LooseVersion(self.version)

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
        if self.version and (self.eddy or self.cuda_version):
            raise ValueError("version cannot be specified with eddy and/or "
                             "cuda_version.")
        if not self.version and not self.eddy:
            raise ValueError("version or eddy must be specfied.")
        if not self.eddy and self.cuda_version:
            raise ValueError("cuda_version can only be specified when eddy is "
                             "specified.")
        return True

    def _create_cmd(self):
        """Return full Dockerfile instructions to install FSL."""
        comment = ("#-----------------------------------------------------------"
                   "\n# Install FSL v{}"
                   "\n# FSL is non-free. If you are considering commerical use"
                   "\n# of this Docker image, please consult the relevant license:"
                   "\n# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence"
                   "\n#-----------------------------------------------------------")
        if self.version:
            comment = comment.format(self.version)
        elif self.eddy:
            comment = comment.format(self.eddy)

        if self.eddy:
            url = self._get_eddy_5011_url()
            cmd = self.install_eddy_5011(url)
        elif self.use_binaries:
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

    def _install_binaries_deps(self):
        """Return command to install FSL dependencies."""
        pkgs = {'apt': "bc dc",
                'yum': "bc"}

        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        return cmd.format(pkgs=pkgs[self.pkg_manager])

    def install_binaries(self, url):
        """Return Dockerfile instructions to install FSL using binaries hosted
        on FSL's website.
        """
        from neurodocker.generate import _add_to_entrypoint

        cmd = self._install_binaries_deps()
        cmd += ('\n&& echo "Downloading FSL ..."'
                '\n&& curl -sSL {}'
                '\n| tar zx -C /opt'.format(url))

        if self.version >= LooseVersion('5.0.10'):
            fsl_python = "/opt/fsl/etc/fslconf/fslpython_install.sh"
            cmd += "\n&& /bin/bash {} -q -f /opt/fsl".format(fsl_python)

        ent_cmds = ["echo Some packages in this Docker container are non-free",
                    ("echo If you are considering commercial use of this"
                     " container, please consult the relevant license:"),
                    "echo https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence",
                    "source $FSLDIR/etc/fslconf/fsl.sh"]
        cmd += "\n&& {}".format(_add_to_entrypoint(ent_cmds, with_run=False))
        cmd = indent("RUN", cmd)

        env_cmd = ("FSLDIR=/opt/fsl"
                   "\nPATH=/opt/fsl/bin:$PATH")
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((cmd, env_cmd))

    def _get_eddy_5011_url(self):
        """Return URL of FSL eddy 5.0.11 pre-release."""
        # This function should probably be removed once FSL v5.0.11 is released
        base_url = ("https://fsl.fmrib.ox.ac.uk/fsldownloads/patches/"
                    "eddy-patch-fsl-5.0.11/centos6/")
        cuda_versions = {
            '6.5': 'eddy_cuda6.5',
            '7.0': 'eddy_cuda7.0',
            '7.5': 'eddy_cuda7.5',
            '8.0': 'eddy_cuda8.0',
        }
        if self.cuda_version is None:
            filename = "eddy_openmp"
        else:
            filename = cuda_versions.get(self.cuda_version, None)
            if filename is None:
                raise ValueError("Valid CUDA versions are {}"
                                 .format(', '.join(cuda_versions.keys())))
        return urljoin(base_url, filename)

    def install_eddy_5011(self, url):
        """Return Dockerfile instructions to install FSL eddy 5.0.11
        pre-release.
        """
        from neurodocker.generate import _add_to_entrypoint

        if self.check_urls:
            check_url(url)

        comment = "# Eddy v5.0.11 pre-release"

        pkgs = {'apt': "libgomp1",
                'yum': "libgomp"}

        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        cmd = cmd.format(pkgs=pkgs[self.pkg_manager])

        cmd += ('\n&& mkdir -p /opt/fsl/bin'
                '\n&& cd /opt/fsl/bin'
                '\n&& echo "Downloading FSL eddy..."'
                '\n&& curl -sSLO {}'
                '\n&& ln -sfv eddy_* eddy'
                '\n&& chmod +x eddy').format(url)

        ent_cmds = ["echo Some packages in this Docker container are non-free",
                    ("echo If you are considering commercial use of this"
                     " container, please consult the relevant license:"),
                    "echo https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence"]
        cmd += "\n&& {}".format(_add_to_entrypoint(ent_cmds, with_run=False))

        cmd = indent("RUN", cmd)

        env_cmd = "ENV PATH=/opt/fsl/bin:$PATH"
        return "\n".join((comment, cmd, env_cmd))
