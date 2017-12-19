""""""

from __future__ import absolute_import
import os

from neurodocker.utils import load_yaml

here = os.path.dirname(os.path.realpath(__file__))


def load_global_specs(glob_pattern):
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


_glob_pattern = os.path.join(here, '*.yaml')
global_specs = load_global_specs(_glob_pattern)
