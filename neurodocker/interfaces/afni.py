"""Add Dockerfile instructions to install AFNI.

Homepage: https://afni.nimh.nih.gov/
GitHub repo: https://github.com/afni/afni
Documentation: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/index.html

Notes
-----
- AFNI uses semantic versioning starting from 15.3.00, released on GitHub on
  January 4, 2016. Before this, it is unclear how AFNI was versioned.
- Only the latest binaries exist on AFNI's website.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function

from neurodocker.utils import check_url, indent, manage_pkgs

# find -type f -executable -exec /bin/bash -c "file -i '{}' | grep -q 'x-executable; charset=binary'" \; -print | xargs ldd | sed -n '/not\ found/p' | sed 's/=>.*//' | xargs -n1 | sort | uniq
# docker run --rm -it -e DISPLAY=$(hostname):0 -v /private/tmp/.X11-unix:/tmp/.X11-unix -v ~/Downloads/linux_openmp_64:/opt/afni:ro kaczmarj/ants-deps

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
    check_urls : bool
        If true, raise error if a URL used by this class responds with an error
        code.
    """

    VERSION_TARBALLS = {
        "latest": "https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz",
        "17.2.02": "https://dl.dropbox.com/s/yd4umklaijydn13/afni-Linux-openmp64-v17.2.02.tgz",
        }

    def __init__(self, version, pkg_manager, use_binaries=True,
                 check_urls=True):
        self.version = version
        self.pkg_manager = pkg_manager
        self.use_binaries = use_binaries
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
            'apt': 'gsl-bin libglu1-mesa-dev libglib2.0-0 libglw1-mesa libgomp1'
                   '\nlibjpeg62 libxm4 netpbm tcsh xfonts-base xvfb',
            'yum': 'ed gsl libGLU libgomp libpng12 libXp libXpm netpbm-progs'
                   '\nopenmotif R-devel tcsh xorg-x11-fonts-misc'
                   ' xorg-x11-server-Xvfb',
        }
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
               "\n&& ln /usr/lib/x86_64-linux-gnu/libgsl.so.19"
               " /usr/lib/x86_64-linux-gnu/libgsl.so.0"
               "\n|| true"
               "".format(**manage_pkgs[self.pkg_manager]).format(pkgs=pkgs))

        if self.pkg_manager == "apt":
            # libxp was removed after ubuntu trusty.
            deb_url = ('http://mirrors.kernel.org/debian/pool/main/libx/'
                       'libxp/libxp6_1.0.2-2_amd64.deb')
            cmd += ("\n&& apt-get install -yq libxp6"
                    '\n|| /bin/bash -c "'
                    '\n   curl -o /tmp/libxp6.deb -sSL {}'
                    '\n   && dpkg -i /tmp/libxp6.deb && rm -f /tmp/libxp6.deb"'
                    ''.format(deb_url))

        cmd += ("\n&& {clean}"
                '\n&& echo "Downloading AFNI ..."'
                "\n&& mkdir -p /opt/afni"
                "\n&& curl -sSL --retry 5 {}"
                "\n| tar zx -C /opt/afni --strip-components=1"
                "\n&& cp /opt/afni/AFNI.afnirc $HOME/.afnirc"
                "\n&& cp /opt/afni/AFNI.sumarc $HOME/.sumarc"
                "".format(url, **manage_pkgs[self.pkg_manager]))
        cmd = indent("RUN", cmd)

        env_cmd = "PATH=/opt/afni:$PATH"
        env_cmd = indent("ENV", env_cmd)

        return "\n".join((cmd, env_cmd))
