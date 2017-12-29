""""""

from neurodocker.interfaces._base import _BaseInterface

_installation_implementations = {
    ii._name: ii for ii in _BaseInterface.__subclasses__()
}

# TODO: add common methods like `--install` here. Reference them in the
# Dockerfile and SingularityRecipe implementation classes.
