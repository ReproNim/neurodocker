#!/usr/bin/env python3

import csv
from collections import namedtuple
import os
import subprocess

NEURODOCKER_EXE = "docker run --rm kaczmarj/neurodocker:test generate"


def load_params(filepath):
    """Return list of namedtuple objects, where each namedtuple contains the
    parameters to generate one Dockerfile or Singularity recipe.
    """
    with open(filepath, newline='') as infile:
        reader = csv.reader(infile)
        param = namedtuple("param", next(reader))
        return [d for d in map(param._make, reader)]


def _format_generate_args(param):
    """Return string of arguments to `neurodocker generate` given a namedtuple.
    """
    if param.container == 'singularity':
        base = "docker://" + param.base
    else:
        base = param.base

    cmd = (
        "{p.container} -b {b} -p {p.pkg_manager} --{p.software}"
        .format(b=base, p=param)
    )

    if param.version != 'None' and param.version:
        cmd += " version={}".format(param.version)

    if param.method != 'None' and param.method:
        cmd += " method={}".format(param.method)

    if param.args != 'None' and param.args:
        cmd += " {}".format(param.args)

    return cmd


def _get_dockerfile_name(param):
    return "{p.software}.{p.method}.{p.base}.{p.container}".format(p=param)


def format_generate_cmd(param):
    """Return string of neurodocker generate command."""
    return " ".join((NEURODOCKER_EXE, _format_generate_args(param)))


def generate_and_save_fn(save_dir=None):
    if save_dir is None:
        save_dir = os.env['HOME']

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    def generate_and_save(param):
        name = _get_dockerfile_name(param)
        filepath = os.path.join(save_dir, name)

        cmd = format_generate_cmd(param)

        container_spec = subprocess.check_output(cmd, shell=True)

        with open(filepath, 'wb') as fp:
            fp.write(container_spec)

        return filepath

    return generate_and_save


if __name__ == '__main__':

    import sys

    here = os.path.dirname(os.path.abspath(__file__))
    csv_filepath = os.path.join(here, '_test_params.csv')

    params = load_params(csv_filepath)

    save_path = sys.argv[1]
    generate_and_save = generate_and_save_fn(save_path)

    for filepath in map(generate_and_save, params):
        print(filepath)
