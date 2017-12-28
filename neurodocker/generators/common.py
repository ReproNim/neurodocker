""""""

from neurodocker.interfaces._base import _BaseInterface

_installation_implementations = {
    ii._name: ii for ii in _BaseInterface.__subclasses__()
}
