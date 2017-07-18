"""Package utility functions."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function
import json
import logging

import requests


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


def _list_to_dict(list_of_kv):
    """Convert list of [key, value] pairs to a dictionary."""
    if list_of_kv is not None:
        list_of_kv = [item for sublist in list_of_kv for item in sublist]

        for kv_pair in list_of_kv:
            if len(kv_pair) != 2:
                raise ValueError("Error in arguments '{}'. Did you forget "
                                 "the equals sign?".format(kv_pair[0]))
            if not kv_pair[-1]:
                raise ValueError("Option required for '{}'".format(kv_pair[0]))

        return {k: v for k, v in list_of_kv}


def _string_vals_to_bool(dictionary):
    """Convert string values to bool."""
    import re

    bool_vars = ['use_binaries', 'use_installer', 'use_neurodebian']

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


def set_log_level(logger, level):
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
