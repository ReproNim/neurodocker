""""""

from neurodocker.interfaces._base import _BaseInterface


class AFNI(_BaseInterface):
    """Create instance of AFNI object."""

    _name = 'afni'
    _pretty_name = 'AFNI'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)
