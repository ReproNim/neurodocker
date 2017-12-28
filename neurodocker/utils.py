"""Package utility functions."""


# TODO: move this function to neurodocker.generate.py
def _string_vals_to_bool(dictionary):
    """Convert string values to bool."""
    import re

    bool_vars = ['use_binaries', 'use_installer', 'use_neurodebian',
                 'add_to_path', 'min']

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


# TODO: move this function to neurodocker.generate.py
def _string_vals_to_list(dictionary):
    """Convert string values to lists."""
    list_keys = ['conda_install', 'pip_install']

    for kk in list_keys:
        if kk in dictionary.keys():
            dictionary[kk] = " ".join((jj.strip() for jj
                                       in dictionary[kk].split()))


# TODO: move this function to neurodocker.generate.py
def _namespace_to_specs(namespace):
    """Return dictionary of specifications from namespace."""
    from neurodocker.generate import dockerfile_implementations

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
        if instruction in dockerfile_implementations['software'].keys():
            _string_vals_to_bool(options)
            _string_vals_to_list(options)

    specs = {'pkg_manager': namespace.pkg_manager,
             'check_urls': namespace.check_urls,
             'instructions': instructions, }

    return specs


def is_url(string):
    from urllib.parse import urlparse

    result = urlparse(string)
    return (result.scheme and result.netloc)


def load_json(filepath, **kwargs):
    """Load JSON file `filepath` as dictionary. `kwargs` are keyword arguments
    for `json.load()`.
    """
    import json

    with open(filepath, 'r') as fp:
        return json.load(fp, **kwargs)


def load_yaml(filepath, **kwargs):
    """Return dictionary from YAML file."""
    import yaml

    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader

    with open(filepath) as fp:
        return yaml.load(fp, Loader=Loader, **kwargs)


def save_json(obj, filepath, indent=4, **kwargs):
    """Save `obj` to JSON file `filepath`. `kwargs` are keyword arguments for
    `json.dump()`.
    """
    import json

    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=indent, **kwargs)
        fp.write('\n')


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
    import logging

    logging_levels = {'DEBUG': logging.DEBUG,
                      'INFO': logging.INFO,
                      'WARNING': logging.WARNING,
                      'ERROR': logging.ERROR,
                      'CRITICAL': logging.CRITICAL}
    try:
        level = logging_levels[level.upper()]
        logger.setLevel(level)
    except KeyError:
        raise ValueError("invalid level '{}'".format(level))
