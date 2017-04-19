"""Package utility functions."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
import json
import logging
import sys
import warnings

import requests


# Templates for installing packages and cleaning up with apt and yum.
manage_pkgs = {'apt': {'install': ('apt-get update -qq && apt-get install -yq '
                                   '--no-install-recommends {pkgs}'),
                       'remove': 'apt-get purge -y --auto-remove {pkgs}',
                       'clean': ('apt-get clean '
                                '&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*'),},
               'yum': {'install': 'yum install -y -q {pkgs}',
                       # Trying to uninstall ca-certificates breaks things.
                       'remove': 'yum remove -y $(echo "{pkgs}" | sed "s/ca-certificates//g")',
                       'clean': ('yum clean packages '
                                 '&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*'),},
                }

# Create logger.
# TODO: move this to main program.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)  # Print to console.
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def set_log_level(level):
    """Set logger verbosity.

    Parameters
    ----------
    level: {'debug', 'info', 'warning', 'error', 'critical}
        The level at which to print messages. Case-insensitive.
    """
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


def check_url(url, timeout=5, **kwargs):
    """Return true if `url` is returns a status code < 400. Otherwise, log
    warning and return false. `kwargs` are arguments for `requests.get()`.

    Parameters
    ----------
    url : str
        The URL to check.
    timeout : numeric
        Number of seconds to wait for response from server.
    """
    try:
        request = requests.head(url, timeout=timeout, **kwargs)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        warnings.warn("Connection timed out. Is the website down? ({})"
                      "".format(url))
        return False
    if request.status_code < 400:
        return True
    else:
        warnings.warn("URL ({}) returned status code {}."
                      "".format(url, request.status_code))
        return False


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


def add_neurodebian(os_codename, full=True, check_urls=True):
    """Return instructions to add NeuroDebian to Dockerfile.

    Parameters
    ----------
    os_codename : str
        Operating system codename (e.g., 'zesty', 'jessie'). Used in the
        NeuroDebian url: http://neuro.debian.net/lists/OS_CODENAME.us-nh.full.
    full : bool
        If true, use the full NeuroDebian sources. If false, use the libre
        sources.
    check_urls : bool
        If true, throw warning if URLs relevant to the installation cannot be
        reached.
    """
    suffix = "full" if full else "libre"
    neurodebian_url = ("http://neuro.debian.net/lists/{}.us-nh.{}"
                       "".format(os_codename, suffix))
    if check_urls:
        check_url(neurodebian_url)

    cmd = ("deps='dirmngr wget'\n"
           "&& {install}\n"
           "&& wget -O- {url} >> "
           "/etc/apt/sources.list.d/neurodebian.sources.list\n"
           "&& apt-key adv --recv-keys --keyserver "
           "hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9\n"
           "&& apt-get update\n"
           "&& {remove}\n"
           "&& {clean}".format(url=neurodebian_url, **manage_pkgs['apt']))
    cmd = cmd.format(pkgs="$deps")
    return indent("RUN", cmd)
