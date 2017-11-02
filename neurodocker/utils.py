"""Package utility functions."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, division, print_function
import json
import logging
import string

import requests


dockerfile_instructions = ['ADD', 'ARG', 'CMD', 'COPY', 'ENTRYPOINT', 'ENV',
                           'EXPOSE', 'FROM', 'HEALTHCHECK', 'LABEL',
                           'MAINTAINER', 'ONBUILD', 'RUN', 'SHELL',
                           'STOPSIGNAL', 'USER', 'VOLUME', 'WORKDIR']


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


class OptionalStrFormatter(string.Formatter):
    # https://stackoverflow.com/a/20250018/5666087
    """"""
    def __init__(self, missing_optional="", optional_prefix="optional_"):
        self.missing_optional = missing_optional
        self.optional_prefix = optional_prefix

    def get_field(self, field_name, args, kwargs):
        # Handle missing fields
        try:
            return super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            if field_name.startswith(self.optional_prefix):
                return None, field_name
            else:
                err = "keyword argument '{}' is required".format(field_name)
                raise KeyError(err)

    def format_field(self, value, spec):
        if value is None:
            return self.missing_optional
        else:
            return super().format_field(value, spec)


optional_formatter = OptionalStrFormatter()

# NEW


def get_string_format_keys(string):
    from string import Formatter
    return set(ii[1] for ii in Formatter().parse(string)
               if ii[1] is not None)


def indent_str(string, indent=4, indent_first_line=False):
    separator = "\n" + " " * indent
    if indent_first_line:
        return separator + separator.join(string.split('\n'))
    else:
        return separator.join(string.split('\n'))


def _indent_pkgs(pkgs, indent, sort):
    separator = "\n" + " " * indent
    if sort:
        return separator + separator.join(sorted(pkgs))
    else:
        return separator + separator.join(pkgs)


def _yum_install(pkgs, flags=None, indent=4, sort=False):
    """Return command to install `pkgs` with `yum`."""
    if flags is None:
        flags = "-q"
    install = "yum install -y {flags}".format(flags=flags)
    clean = ("\n&& yum clean packages"
             "\n&& rm -rf /var/cache/yum/* /tmp/* /var/tmp/*")
    return install + _indent_pkgs(pkgs, indent=indent, sort=sort) + clean


def _apt_get_install(pkgs, flags=None, indent=4, sort=False):
    """Return command to install `pkgs` with `apt-get`."""
    if flags is None:
        flags = "-q --no-install-recommends"
    install = ("apt-get update -qq"
               "\n&& apt-get install -y {flags}").format(flags=flags)
    clean = ("\n&& apt-get clean"
             "\n&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*")
    return install + _indent_pkgs(pkgs, indent=indent, sort=sort) + clean


def install(pkg_manager, pkgs, flags=None, indent=4, sort=False):
    installers = {
        'apt': _apt_get_install,
        'yum': _yum_install,
    }
    installer = installers.get(pkg_manager, None)
    if installer is None:
        err = "installation instructions not known for package manager '{}'."
        err = err.format(pkg_manager)
        raise ValueError(err)
    return installer(pkgs=pkgs, flags=flags, indent=indent, sort=sort)


def add_slashes(string):
    lines = string.split('\n')
    for ii, line in enumerate(lines):
        if ii + 1 == len(lines):
            continue
        elif not lines[ii + 1]:
            continue
        elif lines[ii + 1].split()[0] in dockerfile_instructions:
            continue
        elif lines[ii + 1].startswith("#"):
            continue
        lines[ii] = line + "  \\"
    return '\n'.join(lines)


def comment(string):
    split_point = "\n"
    comment = "# "
    return split_point.join((comment + ll for ll in string.split(split_point)))


# END NEW


# def _indent_pkgs(line_len, pkgs):
#     cmd = " {first_pkg}".format(first_pkg=pkgs[0])
#     separator = "\n" + " " * (line_len + 1)
#     return separator.join((cmd, *pkgs[1:]))


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


def load_yaml(filepath):
    import yaml
    with open(filepath) as fp:
        return yaml.load(fp)


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
