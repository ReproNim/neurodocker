""""""

from neurodocker.interfaces._base import _BaseInterface


class AFNI(_BaseInterface):
    """Create instance of AFNI object."""

    _name = 'afni'
    _pretty_name = 'AFNI'

    def __init__(self, *args, install_python2=False, install_python3=False,
                 install_r=False, install_r_pkgs=False, **kwargs):
        self.install_python2 = install_python2
        self.install_python3 = install_python3
        self.install_r = install_r
        self.install_r_pkgs = install_r_pkgs
        super().__init__(self._name, *args, **kwargs)

        if self.install_python2:
            self._dependencies.append('python')
        if self.install_python3:
            self._dependencies.append('python3')
        if self.install_r:
            r = {
                'apt': ['r-base', 'r-base-dev'],
                'yum': ['R-devel'],
            }
            self._dependencies.extend(r[self._pkg_manager])

        if self.install_r_pkgs and not self.install_r:
            raise ValueError(
                "option `install_r=True` must be specified if"
                " `install_r_pkgs=True`."
            )

    def _install_r_pkgs(self):
        """Return string of instructions to install AFNI's R packages."""
        return "{{ afni.install_path }}/rPkgsInstall -pkgs ALL"


class ANTs(_BaseInterface):
    """Create instance of ANTs object."""

    _name = 'ants'
    _pretty_name = 'ANTs'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class Convert3D(_BaseInterface):
    """Create instance of Convert3D object."""

    _name = 'convert3d'
    _pretty_name = 'Convert3D'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class Dcm2niix(_BaseInterface):
    """Create instance of Dcm2niix object."""

    _name = 'dcm2niix'
    _pretty_name = 'dcm2niix'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class FreeSurfer(_BaseInterface):
    """Create instance of FreeSurfer object."""

    _name = 'freesurfer'
    _pretty_name = 'FreeSurfer'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class FSL(_BaseInterface):
    """Create instance of FSL object."""

    _name = 'fsl'
    _pretty_name = 'FSL'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class MINC(_BaseInterface):
    """Create instance of MINC object."""

    _name = 'minc'
    _pretty_name = 'MINC'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class Miniconda(_BaseInterface):
    """Create instance of Miniconda object."""

    _name = 'miniconda'
    _pretty_name = 'Miniconda'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class MRtrix3(_BaseInterface):
    """Create instance of MRtrix3 object."""

    _name = 'mrtrix3'
    _pretty_name = 'MRtrix3'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class NeuroDebian(_BaseInterface):
    """Create instance of NeuroDebian object."""

    _name = 'neurodebian'
    _pretty_name = 'NeuroDebian'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class PETPVC(_BaseInterface):
    """Create instance of PETPVC object."""

    _name = 'petpvc'
    _pretty_name = 'PETPVC'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class SPM12(_BaseInterface):
    """Create instance of SPM object."""

    _name = 'spm12'
    _pretty_name = 'SPM12'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)
