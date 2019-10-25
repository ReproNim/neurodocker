""""""

from copy import deepcopy
import os
import posixpath

import jinja2

from neurodocker.utils import load_yaml

GENERIC_VERSION = 'generic'

apt_install = """apt-get update -qq
apt-get install -y {{ apt_opts|default('-q --no-install-recommends') }} \\\
{% for pkg in pkgs %}
    {% if not loop.last -%}
    {{ pkg }} \\\
    {%- else -%}
    {{ pkg }}
    {%- endif -%}
{% endfor %}
apt-get clean
rm -rf /var/lib/apt/lists/*
"""
apt_install = jinja2.Template(apt_install)

yum_install = """yum install -y {{ yum_opts|default('-q') }} \\\
{% for pkg in pkgs %}
    {% if not loop.last -%}
    {{ pkg }} \\\
    {%- else -%}
    {{ pkg }}
    {%- endif -%}
{% endfor %}
yum clean packages
rm -rf /var/cache/yum/*
"""
yum_install = jinja2.Template(yum_install)

deb_install = """{% for deb_url in debs -%}
curl -sSL --retry 5 -o /tmp/toinstall.deb {{ deb_url }}
dpkg -i /tmp/toinstall.deb
rm /tmp/toinstall.deb
{% endfor -%}
apt-get install -f
apt-get clean
rm -rf /var/lib/apt/lists/*
"""
deb_install = jinja2.Template(deb_install)


def _load_global_specs():

    def load_global_specs(glob_pattern):
        import glob

        def load_interface_spec(filepath):
            _, filename = os.path.split(filepath)
            key, _ = os.path.splitext(filename)
            return key, load_yaml(filepath)

        interface_yamls = glob.glob(glob_pattern)
        instructions = {}
        for ff in interface_yamls:
            key, data = load_interface_spec(ff)
            instructions[key] = data
        return instructions

    base_path = os.path.dirname(os.path.realpath(__file__))
    glob_pattern = os.path.join(base_path, '..', 'templates', '*.yaml')
    return load_global_specs(glob_pattern)


_global_specs = _load_global_specs()


def _interface_exists_in_yaml(name):
    return name in _global_specs.keys()


class _Resolver:
    """
    Parameters
    ----------
    d : dict
    """

    def __init__(self, d):
        self._d = d
        self._generic_only = self._d.keys() == {GENERIC_VERSION}

    @property
    def versions(self):
        return set(self._d.keys())

    def version_exists(self, version):
        if self._generic_only:
            return True
        else:
            return version in self.versions

    def check_version_exists(self, version):
        if not self.version_exists(version):
            raise ValueError("version '{}' not found.".format(version))

    def get_version_key(self, version):
        """Return version key to use given a specific version. For example,
        if a dictionary only has instructions for version 'generic', will
        return 'generic' given any version string.

        Raises
        ------
        `ValueError` if no key could be found for requested version.
        """
        if self._generic_only:
            return GENERIC_VERSION
        else:
            self.check_version_exists(version)
            return version

    def version_has_method(self, version, method):
        version_key = self.get_version_key(version)
        return method in self._d[version_key].keys()

    def check_version_has_method(self, version, method):
        if not self.version_has_method(version, method):
            raise ValueError(
                "version '{}' does not have method '{}'"
                .format(version, method)
            )

    def version_method_has_instructions(self, version, method):
        version_key = self.get_version_key(version)
        self.check_version_has_method(version_key, method)
        return 'instructions' in self._d[version_key][method].keys()

    def check_version_method_has_instructions(self, version, method):
        if not self.version_method_has_instructions(version, method):
            raise ValueError(
                "installation method '{}' for version '{}' does not have an"
                " 'instructions' key.".format(method, version)
            )

    def binaries_has_url(self, version):
        version_key = self.get_version_key(version)
        if self.version_has_method(version_key, 'binaries'):
            try:
                urls = self._d[version_key]['binaries']['urls'].keys()
                return version in urls or "*" in urls
            except KeyError:
                raise ValueError(
                    "no binary URLs defined for version '{}'".format(version)
                )
        else:
            raise ValueError(
                "no binary installation method defined for version '{}"
                .format(version)
            )

    def check_binaries_has_url(self, version):
        if not self.binaries_has_url(version):
            version_key = self.get_version_key(version)
            valid_vers = self._d[version_key]['binaries']['urls']
            raise ValueError(
                "URL not found for version '{}'. Valid versions are {}"
                .format(version, ', '.join(valid_vers))
            )

    def binaries_url(self, version):
        self.check_binaries_has_url(version)
        version_key = self.get_version_key(version)
        urls = self._d[version_key]['binaries']['urls']
        if version in urls:
            return urls[version]
        return urls["*"].format(version)


class _BaseInterface:
    """Base class for interface objects."""

    def __init__(self, name, version, pkg_manager, method='binaries',
                 install_path=None, **kwargs):
        self._name = name
        self._version = version
        self._pkg_manager = pkg_manager
        self._method = method
        self._install_path = install_path
        self.__dict__.update(**kwargs)

        if not _interface_exists_in_yaml(self._name):
            raise ValueError(
                "No YAML entry for package '{}'".format(self._name)
            )
        self._resolver = _Resolver(_global_specs[self._name])

        self._version_key = self._resolver.get_version_key(self._version)
        self._resolver.check_version_exists(self._version)
        self._resolver.check_version_has_method(self._version, self._method)
        self._resolver.check_version_method_has_instructions(
            self._version, self._method
        )

        if method == 'binaries':
            self.binaries_url = self._resolver.binaries_url(self._version)

        self._instance_specs = deepcopy(
            _global_specs[self._name][self._version_key][self._method]
        )

        self._run = self._instance_specs['instructions']
        self._dependencies = self._get_dependencies()

        self._env = self._instance_specs.get('env', None)

        # Set default curl options for all interfaces.
        self.__dict__.setdefault("curl_opts", "-fsSL --retry 5")

    @property
    def _pretty_name(self):
        return self.__class__.__name__

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def versions(self):
        return self._resolver.versions

    @property
    def pkg_manager(self):
        return self._pkg_manager

    @property
    def method(self):
        return self._method

    @property
    def env(self):
        return self._env

    @property
    def run(self):
        return self._run

    @property
    def install_path(self):
        if self._install_path is None:
            path = posixpath.join(posixpath.sep, 'opt', '{}-{}')
            return path.format(self._name, self._version)
        return self._install_path

    @property
    def dependencies(self):
        return self._dependencies

    def _get_dependencies(self):
        if 'dependencies' not in self._instance_specs.keys():
            return None
        if self._instance_specs['dependencies'] is None:
            return None
        try:
            deps = self._instance_specs['dependencies'][self._pkg_manager]
            return deps.split() if deps else None
        except KeyError:
            return None

    def _get_debs(self):
        if 'dependencies' not in self._instance_specs.keys():
            return None
        if self._instance_specs['dependencies'] is None:
            return None
        try:
            debs = self._instance_specs['dependencies']['debs']
            return debs if debs else None
        except KeyError:
            return None

    def install_dependencies(self, sort=True):
        if not self.dependencies:
            raise ValueError(
                "No dependencies to install. Add dependencies or remove the"
                " `install_dependencies()` call in the package template."
            )
        pkgs = sorted(self.dependencies) if sort else self.dependencies

        if self.pkg_manager == 'apt':
            # Do not render with `apt_opts` or `yum_opts` if they are not
            # provided, because otherwise, instructions are misprinted.
            apt_opts = self.__dict__.get('apt_opts', None)
            if apt_opts is not None:
                out = apt_install.render(
                    pkgs=pkgs,
                    apt_opts=apt_opts,
                    sort=True)
            else:
                out = apt_install.render(pkgs=pkgs, sort=True)

        elif self.pkg_manager == 'yum':
            yum_opts = self.__dict__.get('yum_opts', None)
            if yum_opts is not None:
                out = yum_install.render(
                    pkgs=pkgs,
                    yum_opts=yum_opts,
                    sort=True)
            else:
                out = yum_install.render(pkgs=pkgs, sort=True)

        return out

    def install_debs(self):
        debs = self._get_debs()
        if not debs:
            raise ValueError(
                "No .deb files to install. Add .deb files or remove the"
                " `install_debs()` call in the package template."
            )
        return deb_install.render(debs=debs)

    def render_run(self):
        return jinja2.Template(self.run).render({self.name: self})

    def render_env(self):
        """Return dictionary with rendered keys and values."""
        return {
            jinja2.Template(k).render({self.name: self}):
            jinja2.Template(v).render({self.name: self})
            for k, v in self.env.items()
        } if self.env else self.env
