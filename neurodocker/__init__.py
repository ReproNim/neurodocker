"""Neurodocker generates containers for neuroimaging.

It includes ReproEnv, which is an extensible, generic container generator.
"""

from neurodocker._version import get_versions
from neurodocker import reproenv  # noqa: F401

__version__ = get_versions()["version"]
del get_versions
