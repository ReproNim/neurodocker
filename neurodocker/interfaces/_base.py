""""""

from copy import deepcopy
import posixpath

import jinja2

from neurodocker.templates import _global_specs

GENERIC_VERSION = 'generic'


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
                return version in urls
            except KeyError:
                raise ValueError(
                    "no binary URLs defined for version '{}".format(version)
                )
        else:
            raise ValueError(
                "no binary installation method defined for version '{}"
                .format(version)
            )

    def check_binaries_has_url(self, version):
        if not self.binaries_has_url(version):
            raise ValueError(
                "URL not found for version '{}'".format(version)
            )


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

        self._instance_specs = deepcopy(
            _global_specs[self._name][self._version_key][self._method]
        )

        self._template = jinja2.Template(self._instance_specs['instructions'])
        self._dependencies = self._get_dependencies()

    def _get_dependencies(self):
        if 'dependencies' not in self._instance_specs.keys():
            return None
        try:
            deps = self._instance_specs['dependencies'][self._pkg_manager]
            return deps.split()
        except KeyError:
            return None

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
    def pkg_manager(self):
        return self._pkg_manager

    @property
    def method(self):
        return self._method

    @property
    def template(self):
        return self._template

    @property
    def install_path(self):
        if self._install_path is None:
            path = posixpath.join(posixpath.sep, 'opt', '{}-v{}')
            return path.format(self._name, self._version)
        return self._install_path

    @property
    def dependencies(self):
        return self._dependencies

    def install_dependencies(self):
        return "INSTALL HERE"

    def render(self):
        return self.template.render({self.name: self})
