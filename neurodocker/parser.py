"""Class to parse specifications for Dockerfile."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function

from neurodocker import SUPPORTED_NI_SOFTWARE
from neurodocker.utils import load_json


class SpecsParser(object):
    """Class to parse specifications for Dockerfile.

    Parameters
    ----------
    filepath : str
        Path to JSON file.
    specs : dict
        Dictionary of specs.
    """
    # Update these as necessary.
    VALID_TOP_LEVEL_KEYS = ['base', 'conda_env', 'software']

    def __init__(self, filepath=None, specs=None):
        if filepath is not None and specs is not None:
            raise ValueError("Specify either `filepath` or `specs`, not both.")
        elif filepath is not None:
            self.specs = load_json(filepath)
        elif specs is not None:
            self.specs = specs

        if 'base' not in self.specs.keys():
            raise ValueError("A base image must be specified in 'base' key.")
        self._validate_keys()
        if 'conda_env' in self.specs.keys():
            self._parse_conda()
        if 'software' in self.specs.keys():
            self._validate_software()

    def __str__(self):
        return str(self.specs)

    def _validate_keys(self):
        """Raise KeyError if unexpected top-level key."""
        unexpected = set(self.specs) - set(self.VALID_TOP_LEVEL_KEYS)
        if unexpected:
            items = ", ".join(unexpected)
            raise KeyError("Unexpected top-level key(s) in input: {}"
                           "".format(items))

    def _parse_conda(self):
        """Parse packages to install with `conda` and/or `pip`."""
        for key, val in self.specs['conda_env'].items():
            if key == "python_version":
                continue
            self.specs['conda_env'][key] = ' '.join(val)

    def _validate_software(self):
        """Parse software version by splitting at '='."""
        software = self.specs['software']
        for pkg, info in software.items():
            if pkg.lower() != pkg:
                software[pkg.lower()] = software.pop(pkg)
            pkg = pkg.lower()
            if pkg not in SUPPORTED_NI_SOFTWARE.keys():
               raise ValueError("The package {} is not supported".format(pkg))
            try:
                if not info['version']:
                    raise ValueError
            except ValueError:
                raise ValueError("Version must be specified for {}".format(pkg))
