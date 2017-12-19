import os

from neurodocker.interfaces.afni import AFNI
from neurodocker.interfaces.ants import ANTs
from neurodocker.interfaces.convert3d import Convert3D
from neurodocker.interfaces.dcm2niix import Dcm2niix
from neurodocker.interfaces.freesurfer import FreeSurfer
from neurodocker.interfaces.fsl import FSL
from neurodocker.interfaces.miniconda import Miniconda
from neurodocker.interfaces.mrtrix import MRtrix3
from neurodocker.interfaces.neurodebian import NeuroDebian
from neurodocker.interfaces.spm import SPM
from neurodocker.interfaces.minc import MINC
from neurodocker.interfaces.petpvc import PETPVC

from neurodocker.utils import load_yaml


def load_global_specs():

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

    base_path = os.path.dirname(os.path.realpath(__file__))
    glob_pattern = os.path.join(base_path, '..', 'templates', '*.yaml')
    return _load_global_specs(glob_pattern)


_global_specs = load_global_specs()
