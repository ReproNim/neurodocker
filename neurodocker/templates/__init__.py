""""""

from __future__ import absolute_import
import os

from neurodocker.utils import load_yaml


def _load_global_specs(glob_pattern):
    import glob

    def _load_interface_spec(filepath):
        _, filename = os.path.split(filepath)
        key, _ = os.path.splitext(filename)
        return key, load_yaml(filepath)

    interface_yamls = glob.glob(glob_pattern)
    instructions = {}
    for ff in interface_yamls:
        key, data = _load_interface_spec(ff)
        instructions[key] = data
    return instructions


def load_global_specs():
    base_path = os.path.dirname(os.path.realpath(__file__))
    glob_pattern = os.path.join(base_path, '*.yaml')
    return _load_global_specs(glob_pattern)


_global_specs = load_global_specs()
