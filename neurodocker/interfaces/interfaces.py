""""""

from neurodocker.interfaces._base import _BaseInterface


class _Header(_BaseInterface):
    """Create instance of _Header oject."""

    _name = "_header"

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


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


class MatlabMCR(_BaseInterface):
    """Create instance of MatlabMCR object."""

    _name = 'matlabmcr'
    _pretty_name = "MATLAB MCR"

    _mcr_versions = {
        '2017b': '93',
        '2017a': '92',
        '2016b': '91',
        '2016a': '901',
        '2015b': '90',
        '2015a': '85',
        '2014b': '84',
        '2014a': '83',
        '2013b': '82',
        '2013a': '81',
        '2012b': '80',
        '2012a': '717',
        '2010a': '713',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)

    @property
    def mcr_version(self):
        try:
            return "v{}".format(self._mcr_versions[self.version])
        except KeyError:
            raise ValueError(
                "Matlab MCR version not known for Matlab version '{}'."
                .format(self.version)
            )


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

    _installed = False
    _environments = set()

    def __init__(self, *args, conda_install=None, pip_install=None, **kwargs):
        self.conda_install = conda_install
        self.pip_install = pip_install

        kwargs.setdefault('version', 'latest')
        super().__init__(self._name, *args, **kwargs)

    def render_run(self):
        out = super().render_run()
        Miniconda._installed = True
        Miniconda._environments.add(self.env_name)
        return out


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

    _servers = {
        'australia': 'au',
        'china-tsinghua': 'cn-bj1',
        'china-scitech': 'cn-bj2',
        'china-zhejiang': 'cn-zj',
        'germany-munich': 'de-m',
        'germany-magdeburg': 'de-md',
        'greece': 'gr',
        'japan': 'jp',
        'usa-ca': 'us-ca',
        'usa-nh': 'us-nh',
        'usa-tn': 'us-tn',
    }

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

        matlabmcr_version = self.binaries_url[-9:-4]
        self.matlabmcr_obj = MatlabMCR(matlabmcr_version, self.pkg_manager)

    def render_run(self):
        return "\n".join(
            (self.matlabmcr_obj.render_run(), super().render_run())
        )

    def render_env(self):
        """Return dictionary with rendered keys and values."""
        return {**super().render_env(), **self.matlabmcr_obj.render_env()}
