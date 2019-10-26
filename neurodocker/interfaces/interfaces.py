""""""

import posixpath

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

    def __init__(self,
                 *args,
                 install_python2=False,
                 install_python3=False,
                 install_r=False,
                 install_r_pkgs=False,
                 **kwargs):
        self.install_python2 = install_python2
        self.install_python3 = install_python3
        self.install_r = install_r
        self.install_r_pkgs = install_r_pkgs
        super().__init__(self._name, *args, **kwargs)

        if self.install_python2:
            self._dependencies.append('python')
        if self.install_python3:
            self._dependencies.append('python3')
        if self.install_r or self.install_r_pkgs:
            r = {
                'apt': ['r-base', 'r-base-dev', 'libnlopt-dev'],
                'yum': ['R-devel'],
            }
            self._dependencies.extend(r[self._pkg_manager])


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

    _exclude_paths = (
        'average/mult-comp-cor',
        'lib/cuda',
        'lib/qt',
        'subjects/V1_average',
        'subjects/bert',
        'subjects/cvs_avg35',
        'subjects/cvs_avg35_inMNI152',
        'subjects/fsaverage3',
        'subjects/fsaverage4',
        'subjects/fsaverage5',
        'subjects/fsaverage6',
        'subjects/fsaverage_sym',
        'trctrain',
    )

    # TODO(kaczmarj): add option to add license file.

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)

        if hasattr(self, 'exclude_paths'):
            if isinstance(self.exclude_paths, str):
                self.exclude_paths = self.exclude_paths.split()
        elif 'min' in self.version:
            self.exclude_paths = tuple()
        else:
            self.exclude_paths = FreeSurfer._exclude_paths

        if self.exclude_paths:
            self.exclude_paths = tuple(
                posixpath.join('freesurfer', path)
                for path in self.exclude_paths)


class FSL(_BaseInterface):
    """Create instance of FSL object."""

    _name = 'fsl'
    _pretty_name = 'FSL'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)

        if hasattr(self, 'exclude_paths'):
            if isinstance(self.exclude_paths, str):
                self.exclude_paths = self.exclude_paths.split()
        else:
            self.exclude_paths = tuple()

        if self.exclude_paths:
            self.exclude_paths = tuple(
                posixpath.join('fsl', path) for path in self.exclude_paths)


class MatlabMCR(_BaseInterface):
    """Create instance of MatlabMCR object."""

    _name = 'matlabmcr'
    _pretty_name = "MATLAB MCR"

    _mcr_versions = {
        '2019b': '97',
        '2019a': '96',
        '2018b': '95',
        '2018a': '94',
        '2017b': '93',
        '2017a': '92',
        '2016b': '91',
        '2016a': '901',
        '2015b': '90',
        '2015aSP1': '851',
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
                "Matlab MCR version not known for Matlab version '{}'.".format(
                    self.version))


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
    _environments = {'base'}
    _env_set = False

    def __init__(self,
                 *args,
                 create_env=None,
                 use_env=None,
                 conda_install=None,
                 pip_install=None,
                 yaml_file=None,
                 **kwargs):
        self.create_env = create_env
        self.use_env = use_env
        self.conda_install = conda_install
        self.pip_install = pip_install
        self.yaml_file = yaml_file
        self.env_name = use_env if use_env is not None else create_env
        kwargs.setdefault('version', 'latest')
        super().__init__(self._name, *args, **kwargs)

        if create_env is None and use_env is None:
            raise ValueError("create_env or use_env must be provided")

        if create_env in Miniconda._environments:
            raise ValueError("environment already installed. use `use_env`")

        if not any((conda_install, pip_install, yaml_file)):
            raise ValueError(
                "must conda or pip install packages, or create environment"
                " from yaml file")

        if use_env is not None and yaml_file is not None:
            raise ValueError(
                "cannot use `use_env` with `yaml_file`. `use_env` is meant"
                " for existing environments, and `yaml_file` creates a new"
                " environment.")

        if (yaml_file and conda_install) or (yaml_file and pip_install):
            raise ValueError(
                "cannot conda or pip install when creating environment from"
                " yaml file")

        if self.use_env is not None and self.use_env != "base" and not Miniconda._installed:
            self._environments.add(self.use_env)
            Miniconda._installed = True
            Miniconda._env_set = True

    def render_run(self):
        out = super().render_run()
        Miniconda._installed = True
        Miniconda._environments.add(self.env_name)
        return out

    def render_env(self):
        if not Miniconda._env_set:
            Miniconda._env_set = True
            return super().render_env()


class MINC(_BaseInterface):
    """Create instance of MRIcron object."""

    _name = 'mricron'
    _pretty_name = 'MRIcron'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class MRtrix3(_BaseInterface):
    """Create instance of MRtrix3 object."""

    _name = 'mrtrix3'
    _pretty_name = 'MRtrix3'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class NDFreeze(_BaseInterface):
    """Create instance of NDFreeze object."""

    _name = "ndfreeze"

    def __init__(self, date, *args, **kwargs):
        self.date = date
        super().__init__(
            self._name, version='latest', method='custom', *args, **kwargs)
        if self.pkg_manager != 'apt':
            raise ValueError(
                "nd_freeze cannot be used with a non-apt package manager")


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

    def __init__(self, os_codename, server, full=True, **kwargs):
        self.os_codename = os_codename
        self.server = server

        self._server = NeuroDebian._servers.get(server, None)
        if self._server is None:
            msg = ("Server '{}' not found. Choices are " + ', '.join(
                NeuroDebian._servers.keys()))
            raise ValueError(msg.format(server))

        self._full = 'full' if full else 'libre'

        self.url = 'http://neuro.debian.net/lists/{os}.{srv}.{full}'.format(
            os=self.os_codename, srv=self._server, full=self._full)

        super().__init__(
            self._name,
            version='generic',
            method='custom',
            os_codename=os_codename,
            server=server,
            **kwargs)


class PETPVC(_BaseInterface):
    """Create instance of PETPVC object."""

    _name = 'petpvc'
    _pretty_name = 'PETPVC'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)


class SPM12(_BaseInterface):
    """Create instance of SPM12 object."""

    _name = 'spm12'
    _pretty_name = 'SPM12'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)

        matlabmcr_version = self.binaries_url[-9:-4]
        self.matlabmcr_obj = MatlabMCR(matlabmcr_version, self.pkg_manager)
        self.mcr_path = posixpath.join(self.matlabmcr_obj.install_path,
                                       self.matlabmcr_obj.mcr_version)

    def render_run(self):
        return "\n".join((self.matlabmcr_obj.render_run(),
                          super().render_run()))

    def render_env(self):
        """Return dictionary with rendered keys and values."""
        return {**super().render_env(), **self.matlabmcr_obj.render_env()}


class VNC(_BaseInterface):
    """Create instance of SPM12 object."""

    _name = 'vnc'
    _pretty_name = 'VNC'

    def __init__(self, *args, **kwargs):

        super().__init__(
            self._name, *args, version='generic', method='system', **kwargs)

        if not hasattr(self, "passwd"):
            raise ValueError("`passwd` argument is required for VNC.")
