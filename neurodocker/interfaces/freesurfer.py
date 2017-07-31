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
    min : bool
        If true, install FreeSurfer minimized for recon-all.
    license_path : str
        Relative path to license.txt file. If provided, adds a COPY instruction
        to copy the file into $FREESURFER_HOME (always /opt/freesurfer/).
    use_binaries : bool, str
        If true, uses pre-compiled FreeSurfer binaries. Building from source
        is not yet supported.
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.
    """

    def __init__(self, version, pkg_manager, min=False, license_path=None,
                 use_binaries=True, check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.min = min
        self.license_path = license_path
        self.use_binaries = use_binaries
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install FreeSurfer."""
        comment = ("#--------------------------\n"
                   "# Install FreeSurfer v{}\n"
                   "#--------------------------".format(self.version))

        chunks = [comment]

        if self.min:
            if self.version != "6.0.0":
                raise ValueError("Minimized version is only avialable for"
                                 " FreeSurfer version 6.0.0")
            min_comment = ("# Install version minimized for recon-all"
                           "\n# See https://github.com/freesurfer/freesurfer/issues/70")
            chunks.append(min_comment)
            chunks.append(self.add_min_recon_all())
        elif self.use_binaries:
            chunks.append(self.install_binaries())
        else:
            raise ValueError("Installation via binaries is the only available "
                             "installation method for now.")

        if self.license_path is not None:
            chunks.append(self._copy_license())

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

    def _install_binaries_deps(self):
        """Return command to install FreeSurfer dependencies. Use this for
        FreeSurfer binaries, not if attempting to build FreeSurfer from source.
        """
        pkgs = {'apt': "bc libgomp1 libxmu6 libxt6 tcsh",
                'yum': "bc libgomp libXmu libXt tcsh"}

        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        return cmd.format(pkgs=pkgs[self.pkg_manager])

    def install_binaries(self):
        """Return command to download and install FreeSurfer binaries."""
        url = self._get_binaries_url()

        if self.check_urls and self.version == 'dev':
            raise ValueError("check_urls=True and version='dev' cannot be used "
                             "together. Set check_urls to False.")
        elif self.check_urls:
            check_url(url)

        # https://github.com/nipy/workshops/blob/master/170327-nipype/docker/Dockerfile.complete#L8-L20
        # TODO: allow users to choose which directories to exclude.
        excluded_dirs = ("--exclude='freesurfer/trctrain'"
                         "\n--exclude='freesurfer/subjects/fsaverage_sym'"
                         "\n--exclude='freesurfer/subjects/fsaverage3'"
                         "\n--exclude='freesurfer/subjects/fsaverage4'"
                         "\n--exclude='freesurfer/subjects/fsaverage5'"
                         "\n--exclude='freesurfer/subjects/fsaverage6'"
                         "\n--exclude='freesurfer/subjects/cvs_avg35'"
                         "\n--exclude='freesurfer/subjects/cvs_avg35_inMNI152'"
                         "\n--exclude='freesurfer/subjects/bert'"
                         "\n--exclude='freesurfer/subjects/V1_average'"
                         "\n--exclude='freesurfer/average/mult-comp-cor'"
                         "\n--exclude='freesurfer/lib/cuda'"
                         "\n--exclude='freesurfer/lib/qt'")

        cmd = self._install_binaries_deps()
        cmd += ('\n&& echo "Downloading FreeSurfer ..."'
                "\n&& curl -sSL --retry 5 {url}"
                "\n| tar xz -C /opt\n{excluded}"
                "".format(url=url, excluded=excluded_dirs))

        cmd += ("\n&& sed -i '$isource $FREESURFER_HOME/SetUpFreeSurfer.sh'"
                " $ND_ENTRYPOINT")
        cmd = indent("RUN", cmd)

        env_cmd = "ENV FREESURFER_HOME=/opt/freesurfer"

        return "\n".join((cmd, env_cmd))

    def add_min_recon_all(self):
        """Return Dockerfile instructions to install minimized version of
        recon-all.

        See https://github.com/freesurfer/freesurfer/issues/70 for more
        information.
        """
        cmd = self._install_binaries_deps()
        url = ("https://dl.dropbox.com/s/nnzcfttc41qvt31/"
               "recon-all-freesurfer6-3.min.tgz")
        cmd += ('\n&& echo "Downloading minimized FreeSurfer ..."'
                "\n&& curl -sSL {} | tar xz -C /opt"
                "\n&& sed -i '$isource $FREESURFER_HOME/SetUpFreeSurfer.sh'"
                " $ND_ENTRYPOINT"
                "".format(url))
        cmd = indent("RUN", cmd)
        env_cmd = "ENV FREESURFER_HOME=/opt/freesurfer"
        return "\n".join((cmd, env_cmd))

    def _copy_license(self):
        """Return command to copy local license file into the container. Path
        must be a relative path within the build context.
        """
        import os

        if os.path.isabs(self.license_path):
            raise ValueError("Path to license file must be relative, but "
                             "absolute path was given.")

        comment = ("# Copy license file into image. "
                   "Must be relative path within build context.")
        cmd = ('COPY ["{file}", "/opt/freesurfer/license.txt"]'
               ''.format(file=self.license_path))
        return '\n'.join((comment, cmd))
