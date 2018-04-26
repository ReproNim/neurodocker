"""Package utility functions."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function
import json
import logging

import requests

APT_GET_INSTALL_FLAGS = "-q --no-install-recommends"
YUM_INSTALL_FLAGS = "-q"


# Templates for installing packages and cleaning up with apt and yum.
manage_pkgs = {'apt': {'install': ('apt-get update -qq && apt-get install -yq '
                                   '--no-install-recommends {pkgs}'),
                       'remove': 'apt-get purge -y --auto-remove {pkgs}',
                       'clean': ('apt-get clean\n'
                                '&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*'),},
               'yum': {'install': 'yum install -y -q {pkgs}',
                       # Trying to uninstall ca-certificates breaks things.
                       'remove': 'yum remove -y $(echo "{pkgs}" | sed "s/ca-certificates//g")',
                       'clean': ('yum clean packages\n'
                                 '&& rm -rf /var/cache/yum/* /tmp/* /var/tmp/*'),},
                }


def _indent_pkgs(line_len, pkgs):
    cmd = " {first_pkg}".format(first_pkg=pkgs[0])
    separator = "\n" + " " * (line_len + 1)
    return separator.join((cmd, *pkgs[1:]))


def yum_install(pkgs, flags=None):
    """Return command to install `pkgs` with `yum`."""
    if flags is None:
        flags = YUM_INSTALL_FLAGS
    cmd = "yum install -y {flags}".format(flags=flags)
    line_len = len(cmd)
    return cmd + _indent_pkgs(line_len, pkgs)


def apt_get_install(pkgs, flags=None):
    """Return command to install `pkgs` with `apt-get`."""
    if flags is None:
        flags = APT_GET_INSTALL_FLAGS
    cmd = ("apt-get update -qq"
           "\n&& apt-get install -y {flags}").format(flags=flags)
    line_len = len(cmd.split('\n')[-1])
    return cmd + _indent_pkgs(line_len, pkgs)


def _string_vals_to_bool(dictionary):
    """Convert string values to bool."""
    import re

    bool_vars = ['use_binaries', 'use_installer', 'use_neurodebian',
                 'add_to_path', 'min', 'activate']

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
            dictionary[kk] = " ".join((jj.strip() for jj
                                       in dictionary[kk].split()))


def _count_key_occurence_list_of_tuples(list_of_tuples, key):
    """Return the number of times `key` occurs as a key in `list_of_tuples`."""
    return sum(1 for i, _ in list_of_tuples if i == key)


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
    try:
        from urllib.parse import urlparse  # Python 3
    except ImportError:
        from urlparse import urlparse  # Python 2

    result = urlparse(string)
    return (result.scheme and result.netloc)


def check_url(url, timeout=5, **kwargs):
    """Return true if `url` is returns a status code < 400. Otherwise, raise an
    error. `kwargs` are arguments for `requests.head()`.

    Parameters
    ----------
    url : str
        The URL to check.
    timeout : numeric
        Number of seconds to wait for response from server.
    """
    request = requests.head(url, timeout=timeout, **kwargs)
    request.raise_for_status()
    return True


def indent(instruction, cmd, line_suffix=' \\'):
    """Add Docker instruction and indent command.

    Parameters
    ----------
    instruction : str
        Docker instruction for `cmd` (e.g., "RUN").
    cmd : str
        The command (lines separated by newline character).
    line_suffix : str
        The suffix to append to each line except the last one.

    Returns
    -------
    dockerfile_chunk : str
        Instruction compatible with Dockerfile sytax.
    """
    instruction = instruction.upper()
    amount = len(instruction) + 1
    indent = ' ' * amount
    split_cmd = cmd.splitlines()

    if len(split_cmd) == 1:
        return "{} {}".format(instruction, cmd)

    dockerfile_chunk = ''
    for i, line in enumerate(split_cmd):
        if i == 0:  # First line.
            dockerfile_chunk += "{} {}{}".format(instruction, line, line_suffix)
        # Change the following to use str.join() method.
        elif i == len(split_cmd) - 1:  # Last line.
            dockerfile_chunk += "\n{}{}".format(indent, line)
        else:
            dockerfile_chunk += "\n{}{}{}".format(indent, line, line_suffix)
    return dockerfile_chunk


def load_json(filepath, **kwargs):
    """Load JSON file `filepath` as dictionary. `kwargs` can be keyword
    arguments for `json.load()`.
    """
    with open(filepath, 'r') as fp:
        return json.load(fp, **kwargs)


def save_json(obj, filepath, indent=4, **kwargs):
    """Save `obj` to JSON file `filepath`. `kwargs` can be keyword arguments
    for `json.dump()`.
    """
    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=indent, **kwargs)
        fp.write('\n')


def create_logger():
    """Return Neurodocker logger."""
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
