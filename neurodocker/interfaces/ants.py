""""""

from neurodocker.interfaces._base import _BaseInterface


class ANTs(_BaseInterface):
    """Create instance of ANTs object."""

    _name = 'ants'
    _pretty_name = 'ANTs'

    def __init__(self, *args, **kwargs):
        super().__init__(self._name, *args, **kwargs)
