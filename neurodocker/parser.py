"""Class to parse specifications for Dockerfile."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import inspect

from neurodocker import utils
from neurodocker.generators.common import _installation_implementations
from neurodocker.generators.docker import Dockerfile
from neurodocker.generators.singularity import SingularityRecipe


def _check_for_invalid_keys(keys, valid_keys, where):
    invalid = set(keys) - set(valid_keys)
    if invalid:
        invalid = ", ".join(invalid)
        valid_keys = ", ".join(valid_keys)
        raise KeyError("Unexpected {} key(s) in the specifications "
                       "dictionary: {}. Valid keys are {}."
                       "".format(where, invalid, valid_keys))


class _SpecsParser:
    """Class to parse specifications for Dockerfile.

    This class checks the dictionary of specifications for errors and raises
    an error if it finds one.

    Parameters
    ----------
    specs : dict
        The dictionary of specifications.

    Examples
    --------
    >>> specs = {
    ...     'pkg_manager': 'apt',
    ...     'instructions': [
    ...         ('base', 'ubuntu:17.04'),
    ...         ('ants', {'version': '2.2.0'}),
    ...         ('user', 'neuro'),
    ...         ('miniconda', {'python_version': '3.5'}),
    ...     ],
    ... }
    >>> SpecsParser(specs)
    """
    VALID_TOP_LEVEL_KEYS = [
        'instructions', 'pkg_manager', 'generation_timestamp',
        'neurodocker_version'
    ]

    VALID_INSTRUCTIONS_KEYS = Dockerfile._implementations.keys()

    def __init__(self, specs):
        self.specs = specs
        self._run()

    def _run(self):
        self._validate_keys()
        self._validate_software_options()

    def _validate_keys(self):
        if 'instructions' not in self.specs.keys():
            raise KeyError("The key 'instructions' could not be found in the "
                           "specifications dictionary. The value of this key "
                           " should be a list of tuples specifying the "
                           "Dockerfile instructions.")
        if 'pkg_manager' not in self.specs.keys():
            raise KeyError("The key 'pkg_manager' could not be found in the "
                           "specifications dictionary. The value of this key "
                           " is the Linux package manager.")
        n_base_images = utils._count_key_occurence_list_of_tuples(
            self.specs['instructions'], 'base')
        if n_base_images == 0:
            raise ValueError("A base image must be specified in "
                             "specs['instructions'].")
        if n_base_images > 1:
            raise ValueError("Multiple base images specified. Only one base "
                             "may be specified.")
        if self.specs['instructions'][0][0] != "base":
            raise KeyError("The first item in specs['instructions'] must be "
                           "a tuple ('base', '<base_image>').")

        _check_for_invalid_keys(self.specs.keys(), self.VALID_TOP_LEVEL_KEYS,
                                'top-level')

        instructions_keys = [k for k, _ in self.specs['instructions']]
        _check_for_invalid_keys(instructions_keys,
                                self.VALID_INSTRUCTIONS_KEYS, 'instructions')

    def _validate_software_options(self):
        """Raise ValueError if a key is present that does not belong in a
        function's signature.
        """
        for pkg, opts in self.specs['instructions']:
            if pkg in _installation_implementations.keys():
                func = _installation_implementations[pkg]
                params = list(inspect.signature(func).parameters)
                bad_opts = [opt for opt in opts if opt not in params]
                if bad_opts:
                    bad_opts = ', '.join(bad_opts)
                    raise ValueError("Invalid option(s) found in instructions "
                                     " key '{}': {}. Valid options are {}"
                                     "".format(pkg, bad_opts, params))
