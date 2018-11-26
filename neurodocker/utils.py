"""Package utility functions."""

import sys
import json
import logging
import re

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def _count_key_occurence_list_of_tuples(list_of_tuples, key):
    """Return the number of times `key` occurs as a key in `list_of_tuples`."""
    return sum(1 for i, _ in list_of_tuples if i == key)


def _string_vals_to_bool(dictionary):
    """Convert string values to bool."""
    # TODO: remove unnecessary boolean variables.
    bool_vars = {'activate', 'full', 'start_at_runtime'}
    if dictionary is None:
        return
    for key in dictionary.keys():
        if key in bool_vars:
            if re.search('false', dictionary[key], re.IGNORECASE):
                dictionary[key] = False
            elif re.search('true', dictionary[key], re.IGNORECASE):
                dictionary[key] = True
            else:
                dictionary[key] = bool(int(dictionary[key]))


def _string_vals_to_list(dictionary):
    """Convert string values to lists."""
    list_keys = ['conda_install', 'pip_install']

    for kk in list_keys:
        if kk in dictionary.keys():
            dictionary[kk] = dictionary[kk].split()


def _namespace_to_specs(namespace):
    """Return dictionary of specifications from namespace."""
    from neurodocker.generators.common import _installation_implementations

    instructions = [('base', namespace.base)]

    try:
        for arg in namespace.ordered_args:
            # TODO: replace try-except with stricter logic.
            if arg[0] == 'install':
                instructions.append(arg)
                continue
            try:
                ii = (arg[0], {k: v for k, v in arg[1]})
            except ValueError:
                ii = arg
            instructions.append(ii)
    except AttributeError:
        pass

    # Convert string options that should be booleans to booleans.
    for instruction, options in instructions:
        if instruction in _installation_implementations.keys():
            _string_vals_to_bool(options)
            _string_vals_to_list(options)

    specs = {
        'pkg_manager': namespace.pkg_manager,
        'instructions': instructions,
    }

    # Add nd_freeze
    nd_freeze_idx = _get_index_of_tuple_in_instructions(
        'nd_freeze', specs['instructions'])
    if nd_freeze_idx:
        nd_freeze = specs['instructions'].pop(nd_freeze_idx)
        specs['instructions'].insert(1, nd_freeze)

    return specs


def is_url(string):
    from urllib.parse import urlparse

    result = urlparse(string)
    return (result.scheme and result.netloc)


def load_json(filepath, **kwargs):
    """Load JSON file `filepath` as dictionary. `kwargs` are keyword arguments
    for `json.load()`.
    """
    if filepath == '-':
        return json.load(sys.stdin, **kwargs)

    with open(filepath, 'r') as fp:
        return json.load(fp, **kwargs)


def save_json(obj, filepath, indent=4, **kwargs):
    """Save `obj` to JSON file `filepath`. `kwargs` are keyword arguments for
    `json.dump()`.
    """
    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=indent, **kwargs)
        fp.write('\n')


def load_yaml(filepath, **kwargs):
    """Return dictionary from YAML file."""
    with open(filepath) as fp:
        return yaml.load(fp, Loader=Loader, **kwargs)


def create_logger():
    """Return Neurodocker logger."""
    import logging

    logger = logging.getLogger('neurodocker')
    ch = logging.StreamHandler()
    format_ = '[NEURODOCKER %(asctime)s %(levelname)s]: %(message)s'
    formatter = logging.Formatter(format_)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = create_logger()


def set_log_level(level):
    """Set logger verbosity.

    Parameters
    ----------
    level: {'debug', 'info', 'warning', 'error', 'critical}
        The level at which to print messages. Case-insensitive.
    """
    logging_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    try:
        level = logging_levels[level.upper()]
        logger.setLevel(level)
    except KeyError:
        raise ValueError("invalid level '{}'".format(level))


def get_docker_client(version='auto', **kwargs):
    try:
        import docker
    except ImportError:
        raise ImportError("the docker python package is required for this")
    return docker.from_env(version='auto', **kwargs)


def get_singularity_client():
    try:
        import spython.main
    except ImportError:
        raise ImportError(
            "the singularity python (spython) package is required for this")
    return spython.main.Client


def _get_index_of_tuple_in_instructions(implementation, instructions):
    for j, instr in enumerate(instructions):
        if instr[0] == implementation:
            return j
