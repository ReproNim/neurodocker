""""""

import posixpath

from neurodocker.interfaces._base import _BaseInterface

ND_DIRECTORY = posixpath.join(posixpath.sep, 'neurodocker')
ENTRYPOINT_FILE = posixpath.join(ND_DIRECTORY, 'startup.sh')
SPEC_FILE = posixpath.join(ND_DIRECTORY, 'neurodocker_specs.json')

_installation_implementations = {
    ii._name: ii for ii in _BaseInterface.__subclasses__()
}
