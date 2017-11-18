"""Add Dockerfile instructions to install AFNI.

Homepage: https://afni.nimh.nih.gov/
GitHub repo: https://github.com/afni/afni
Documentation: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/index.html

Notes
-----
- AFNI uses something like semantic versioning starting from 15.3.00, released
  on GitHub on January 4, 2016. Before this, it is unclear how AFNI was
  versioned.
- Only the latest binaries exist on AFNI's website.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs


class AFNI(object):
    """Add Dockerfile instructions to install AFNI.

    Parameters
    ----------
    version : str
        AFNI version. Can be "latest" or version string.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    use_binaries : bool
        If true, uses pre-compiled AFNI binaries. True by default.
    install_r : bool
        If true, install R and R packages for AFNI. This can significantly
        increase container build time.
    install_python2: bool
        If true, install Python 2
    install_python3: bool
        If true, install Python 3
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.
    """

    VERSION_TARBALLS = {
        "latest": "https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz",
        "17.2.02": "https://dl.dropbox.com/s/yd4umklaijydn13/afni-Linux-openmp64-v17.2.02.tgz",
    }

    def __init__(self, version, pkg_manager, use_binaries=True,
                 install_r=False, install_python2=False, install_python3=False,
                 check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
        self.install_r = install_r
        self.install_python2 = install_python2
        self.install_python3 = install_python3
        self.check_urls = check_urls

        self.cmd = self._create_cmd()

    def _create_cmd(self):
        """Return full command to install AFNI."""
        comment = ("#--------------------\n"
                   "# Install AFNI {}\n"
                   "#--------------------".format(self.version))

        if self.use_binaries:
            chunks = [comment, self.install_binaries()]
        else:
            raise ValueError("`use_binaries=True` is the only available "
                             "option at this time.")

        return "\n".join(chunks)

    def _get_binaries_urls(cls, version):
        try:
            return AFNI.VERSION_TARBALLS[version]
        except KeyError:
            raise ValueError("AFNI version not available: {}".format(version))

    def _get_binaries_dependencies(self):
        base_deps = {
            'apt': 'ed gsl-bin libglu1-mesa-dev libglib2.0-0 libglw1-mesa'
                    '\nlibgomp1 libjpeg62 libxm4 netpbm tcsh xfonts-base xvfb',
            'yum': 'ed gsl libGLU libgomp libpng12 libXp libXpm netpbm-progs'
                   '\nopenmotif R-devel tcsh xorg-x11-fonts-misc'
                   ' xorg-x11-server-Xvfb',
        }
        if self.install_python2:
            base_deps['apt'] += ' python'
            base_deps['yum'] += ' python'
        if self.install_python3:
            base_deps['apt'] += ' python3'
            base_deps['yum'] += ' python3'

        return base_deps[self.pkg_manager]

    def install_binaries(self):
        """Return Dockerfile instructions to download and install AFNI
        binaries.
        """
        url = self._get_binaries_urls(self.version)
        if self.check_urls:
            check_url(url)

        pkgs = self._get_binaries_dependencies()

        cmd = ("{install}"
               '\n&& libs_path=/usr/lib/x86_64-linux-gnu'
               '\n&& if [ -f $libs_path/libgsl.so.19 ]; then'
               '\n       ln $libs_path/libgsl.so.19 $libs_path/libgsl.so.0;'
               '\n   fi'
               "".format(**manage_pkgs[self.pkg_manager]).format(pkgs=pkgs))

        if self.pkg_manager == "apt":
            # libxp was removed after ubuntu trusty.
            deb_url = ('http://mirrors.kernel.org/debian/pool/main/libx/'
                       'libxp/libxp6_1.0.2-2_amd64.deb')
            cmd += ('\n&& echo "Install libxp (not in all ubuntu/debian repositories)"'
                    "\n&& apt-get install -yq --no-install-recommends libxp6"
                    '\n|| /bin/bash -c "'
                    '\n   curl --retry 5 -o /tmp/libxp6.deb -sSL {}'
                    '\n   && dpkg -i /tmp/libxp6.deb && rm -f /tmp/libxp6.deb"'
                    ''.format(deb_url))

            deb_url = ('http://mirrors.kernel.org/debian/pool/main/libp/'
                       'libpng/libpng12-0_1.2.49-1%2Bdeb7u2_amd64.deb')
            cmd += ('\n&& echo "Install libpng12 (not in all ubuntu/debian repositories"'
                    "\n&& apt-get install -yq --no-install-recommends libpng12-0"
                    '\n|| /bin/bash -c "'
                    '\n   curl --retry 5 -o /tmp/libpng12.deb -sSL {}'
                    '\n   && dpkg -i /tmp/libpng12.deb && rm -f /tmp/libpng12.deb"'
                    ''.format(deb_url))

            if self.install_r:
                sh_url = ("https://gist.githubusercontent.com/kaczmarj/"
                          "8e3792ae1af70b03788163c44f453b43/raw/"
                          "0577c62e4771236adf0191c826a25249eb69a130/"
                          "R_installer_debian_ubuntu.sh")
                cmd += ('\n&& echo "Install R"'
                        "\n&& apt-get install -yq --no-install-recommends"
                        "\n\tr-base-dev r-cran-rmpi libnlopt-dev"
                        '\n || /bin/bash -c "'
                        '\n    curl --retry 5 -o /tmp/install_R.sh -sSL {}'
                        '\n    && /bin/bash /tmp/install_R.sh"').format(sh_url)

        cmd += ("\n&& {clean}"
                '\n&& echo "Downloading AFNI ..."'
                "\n&& mkdir -p /opt/afni"
                "\n&& curl -sSL --retry 5 {}"
                "\n| tar zx -C /opt/afni --strip-components=1"
                "".format(url, **manage_pkgs[self.pkg_manager]))
        if self.install_r:
            cmd += ("\n&& /opt/afni/rPkgsInstall -pkgs ALL"
                    "\n&& rm -rf /tmp/*")

        cmd = indent("RUN", cmd)

        env_cmd = "PATH=/opt/afni:$PATH"
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((env_cmd, cmd))
