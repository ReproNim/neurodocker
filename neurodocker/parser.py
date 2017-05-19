"""Class to parse specifications for Dockerfile."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import

import inspect


from neurodocker import SUPPORTED_SOFTWARE
from neurodocker.utils import load_json


class SpecsParser(object):
    """Class to parse specifications for Dockerfile.

    Parameters
    ----------
    dict_or_filepath : dict, str
        The dictionary of specifications, or the name of the JSON file with the
        specifications.
    """
    VALID_TOP_LEVEL_KEYS = ['base', 'pkg_manager', 'check_urls']
    VALID_TOP_LEVEL_KEYS.extend(SUPPORTED_SOFTWARE.keys())

    def __init__(self, dict_or_filepath):
        try:
            self.specs = load_json(dict_or_filepath)
        except TypeError:
            self.specs = dict_or_filepath

        self.parse()

    def __str__(self):
        return str(self.specs)

    def parse(self):
        self._validate_keys()
        self.specs = self._remove_nones()
        self._validate_software_opts()
        try:
            self._parse_conda_pip()
        except KeyError:
            pass

    def _validate_keys(self):
        """Raise KeyError if invalid top-level key(s)."""
        if 'base' not in self.specs.keys():
            raise KeyError("A base image must be specified in the key 'base'.")
        if 'pkg_manager' not in self.specs.keys():
            raise KeyError("The Linux package manager must be specified in the "
                           "key 'pkg_manager'.")

        invalid = set(self.specs) - set(self.VALID_TOP_LEVEL_KEYS)
        if invalid:
            invalid = ", ".join(invalid)
            valid = ", ".join(self.VALID_TOP_LEVEL_KEYS)
            raise KeyError("Unexpected top-level key(s) in input: {}. Valid "
                           "keys are {}.".format(invalid, valid))

    def _validate_software_opts(self):
        """Raise ValueError if a key is present that does not belong in a
        functions signature.
        """
        for pkg, opts in self.specs.items():
            if pkg in SUPPORTED_SOFTWARE.keys():
                func = SUPPORTED_SOFTWARE[pkg]
                try:
                    params = list(inspect.signature(func).parameters)
                # Python 2.7 does not have inspect.signature
                except AttributeError:
                    params = inspect.getargspec(func.__init__)[0]
                    params.remove('self')

                bad_opts = [opt for opt in opts if opt not in params]
                if bad_opts:
                    bad_opts = ', '.join(bad_opts)
                    raise ValueError("Invalid option(s) found in key '{}': {}"
                                     "".format(pkg, bad_opts))

    def _remove_nones(self):
        return {k:v for k, v in self.specs.items() if v is not None}

    def _parse_conda_pip(self):
        """Parse packages to install with `conda` and/or `pip`."""
        for key, val in self.specs['miniconda'].items():
            if key == "python_version":
                continue
            if isinstance(val, (list, tuple)):
                self.specs['miniconda'][key] = ' '.join(val)
            if isinstance(val, str):
                self.specs['miniconda'][key] = val
