"""Utility functions."""
from __future__ import absolute_import, division, print_function
from ..utils import logger, load_json


def indent(instruction, cmd, line_suffix=' \\'):
    """Add Docker instruction and indent command.

    Parameters
    ----------
    instruction : str
        Docker instruction for `cmd` (e.g., "RUN").
    cmd : str
        The command (lines separated by newline character.)
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


def _parse_versions(item):
    """Separate package name and version if version is given."""
    if ":" in item:
        return tuple(item.split(":"))
    else:
        return item


def add_neurodebian(os, full=True):
    """Return instructions to add NeuroDebian to Dockerfile.

    Parameters
    ----------
    os : str
        Operating system. See http://neuro.debian.net/.
        Options: 'yakkety', 'xenial', 'trusty', 'precise', 'sid', 'stretch',
                 'jessie', 'wheezy', 'squeeze'
    full : bool
        If true, use the full NeuroDebian sources. If false, use the libre
        sources.
    """
    suffix = "full" if full else "libre"
    neurodebian_url = ("http://neuro.debian.net/lists/{}.us-nh.{}"
                       "".format(os, suffix))
    # Change this to store the key locally.
    cmd = ("RUN curl -sSl {} >> "
           "/etc/apt/sources.list.d/neurodebian.sources.list\n"
           "apt-key adv --recv-keys --keyserver"
           "hkp://pgp.mit.edu:80 0xA5D32F012649A5A9\n"
           "apt-get update".format(neurodebian_url))
    return indent("RUN", cmd, line_suffix=" && \\")


class SpecsParser(object):
    """Class to parse specs for Dockerfile.

    Parameters
    ----------
    filepath : str
        Path to JSON file.
    specs : dict
        Dictionary of specs.
    """
    # Update these as necessary.
    TOP_LEVEL_KEYS = ['base', 'conda-env', 'neuroimaging-software']

    def __init__(self, filepath=None, specs=None):
        if filepath is not None and specs is not None:
            raise ValueError("Specify either `filepath` or `specs`, not both.")
        elif filepath is not None:
            self.specs = load_json(filepath)
        elif specs is not None:
            self.specs = specs

        self._validate_keys()
        self.keys_not_present = set(self.TOP_LEVEL_KEYS) - set(self.specs)

        # Only parse versions if key is present.
        # self.parse_versions('neuroimaging-software')

    def _validate_keys(self):
        """Raise KeyError if unexpected top-level key."""
        unexpected = set(self.specs) - set(self.TOP_LEVEL_KEYS)
        if unexpected:
            items = ", ".join(unexpected)
            raise KeyError("Unexpected top-level key(s) in input: {}"
                           "".format(items))

    def parse_versions(self, key):
        """If <VER> is supplied, convert "<PKG>:<VER>" into tuple
        (<PKG>, <VER>).

        Parameters
        ----------
        key : str
            Key in `self.specs`.
        """
        self.specs[key] = [_parse_versions(item) for item in self.specs[key]]
