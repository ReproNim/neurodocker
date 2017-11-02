""""""

from __future__ import absolute_import

from neurodocker.specs import global_specs
from neurodocker.utils import comment, indent_str, install


class BaseInterface:
    """"""

    def __init__(self, yaml_key, method, version, pkg_manager=None, **kwargs):
        self.yaml_key = yaml_key
        self.method = method
        self.version = version
        self.pkg_manager = pkg_manager
        self.__dict__.update(kwargs)

        self._all_interface_specs = global_specs.get(self.yaml_key, None)
        if self._all_interface_specs is None:
            err = "no yaml entry for program '{}'".format(self.yaml_key)
            raise ValueError(err)

        self._version_in_yaml = self._get_version_in_yaml()
        self._specs = self._all_interface_specs[self._version_in_yaml][self.method]
        self._validate_method()
        self._set_install_path()
        self._base_cmd = self._specs['instructions']

    @property
    def cmd(self):
        return self._create_header() + "\n" + self._create_cmd()

    def _get_version_in_yaml(self):
        import itertools
        from pkg_resources import Distribution, Requirement

        avail_vers = self._all_interface_specs.keys()
        if list(avail_vers) == ['generic']:
            return "generic"
        else:
            avail_vers = [Requirement(self.yaml_key + rr)
                          for rr in avail_vers]

        requested_ver = Distribution(project_name=self.yaml_key,
                                     version=self.version)

        bool_matches = [requested_ver in rr for rr in avail_vers]
        matches = list(itertools.compress(avail_vers, bool_matches))
        print(matches)

        if len(matches) > 1:
            err = "multiple matching versions: " + ", ".join(matches)
            raise ValueError(err)
        elif len(matches) == 1:
            return str(matches[0])
        else:
            err = "no matching versions"
            raise ValueError(err)

    def _get_install_deps_cmd(self):
        """Return command to install dependencies."""
        deps = self._specs.get('dependencies', None)

        if deps is None:
            return None

        deps = deps.get(self.pkg_manager, None)
        if deps is None:
            err = "no dependencies for package manager '{}'."
            raise ValueError(err.format(self.pkg_manager))

        deps = deps.split()
        deps_cmd = install(pkg_manager=self.pkg_manager, pkgs=deps)

        return indent_str(deps_cmd)

    def _set_install_path(self):
        """Set install path if it is not provided."""
        try:
            self.install_path
        except AttributeError:
            self.install_path = "/opt/{}-{}".format(self.yaml_key,
                                                    self.version)

    def _validate_method(self):
        methods = self._all_interface_specs[self._version_in_yaml].keys()
        if self.method not in methods:
            valid_methods = ", ".join(methods)
            err = "invalid installation method: '{}'. Valid methods are {}."
            err = err.format(self.method, valid_methods)
            raise ValueError(err)
        return True

    def _create_cmd(self):
        raise NotImplementedError("this method must be implemented")

    def _create_header(self):
        message = "Installing {} version {}.".format(self.pretty_name,
                                                     self.version)
        border = "-" * len(message)
        uncommented_header = "\n".join((border, message, border))
        return comment(uncommented_header)
