"""Package utility functions."""
from __future__ import absolute_import, division, print_function
import contextlib
import json
import logging
import os.path as op
import sys

try:
    from urllib.request import urlopen, HTTPError, URLError  # Python 3
except ImportError:
    from urllib2 import urlopen, HTTPError, URLError  # Python 2


# Create logger.
logger = logging.getLogger('nipype_regtests')
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


def check_url(url):
    """Return true if `url` is reachable. Otherwise, log warning and return
    false.
    http://stackoverflow.com/a/16778473/5666087
    """
    try:
        # Is `with` necessary? Do we have to close the url?
        # Read http://stackoverflow.com/a/1522709/5666087
        with contextlib.closing(urlopen(url)) as x:
            return True
    except (HTTPError, URLError) as e:
        logger.warning("{} error on URL {}".format(url, e))
        return False
