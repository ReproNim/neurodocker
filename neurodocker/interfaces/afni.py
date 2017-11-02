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

from distutils.version import StrictVersion
from urllib.parse import urljoin

from neurodocker.interfaces._base import BaseInterface
from neurodocker.utils import indent, optional_formatter


VERSION_TARBALLS = {
    "latest": "https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz",
    "17.2.02": "https://dl.dropbox.com/s/yd4umklaijydn13/afni-Linux-openmp64-v17.2.02.tgz",
}


class AFNI(BaseInterface):

    _yaml_key = 'afni'
    pretty_name = 'AFNI'

    def __init__(self, version, method='binaries', **kwargs):
        self.version = version
        self.method = method
        self.__dict__.update(kwargs)

        super().__init__(yaml_key=self._yaml_key,
                         version=version,
                         method=method,
                         **kwargs)

    def _create_cmd(self):
        base_cmd = self._specs['instructions']
        binaries_url = VERSION_TARBALLS.get(self.version, None)
        if self.method == 'binaries' and binaries_url is None:
            err = "{} binaries not available for version '{}'"
            raise ValueError(err.format(self.pretty_name, self.version))

        deps_cmd = self._get_install_deps_cmd(additional_deps='git')

        if self.method == 'source':
            try:
                StrictVersion(self.version)
                self.version = "AFNI_{}".format(self.version)
            except ValueError:
                pass

        cmd = optional_formatter.format(base_cmd,
                                        binaries_url=binaries_url,
                                        install_deps=deps_cmd,
                                        **self.__dict__)
        if self.pkg_manager == 'apt':
            cmd = cmd.strip() + '\n' + _get_debian_only_cmd()
        return cmd


def _get_debian_only_cmd():
    """Return Debian-only installation instructions."""
    url_base = "http://mirrors.kernel.org/debian/pool/main"
    url_xp = urljoin(url_base, "libx/libxp/libxp6_1.0.2-2_amd64.deb")
    url_png = urljoin(url_base, "libp/libpng/libpng12-0_1.2.49-1%2Bdeb7u2_amd64.deb")

    comment = "# Install packages not available in all repositories"
    cmd = """apt-get install -yq --no-install-recommends libxp6
|| /bin/bash -c "
curl --retry 5 -o /tmp/libxp6.deb -sSL {url_xp}
&& dpkg -i /tmp/libxp6.deb && rm -f /tmp/libxp6.deb"
&& echo "Install libpng12 (not in all ubuntu/debian repositories"
&& apt-get install -yq --no-install-recommends libpng12-0
|| /bin/bash -c "
curl -o /tmp/libpng12.deb -sSL {url_png}
&& dpkg -i /tmp/libpng12.deb && rm -f /tmp/libpng12.deb"
&& apt-get clean
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*"""
    cmd = cmd.format(url_xp=url_xp, url_png=url_png)
    return comment + '\n' + indent("RUN", cmd, line_suffix='')
