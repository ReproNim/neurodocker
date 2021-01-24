"""Neurodocker generates containers for neuroimaging.

It includes ReproEnv, which is an extensible, generic container generator.
"""

from pathlib import Path

from neurodocker._version import get_versions
from neurodocker import reproenv  # noqa: F401

__version__ = get_versions()["version"]
del get_versions

# Register neurodocker templates
# TODO: remove registration from the `generate` cli. otherwise we register twice.
for template_path in (Path(__file__).parent / "templates").glob("*.yaml"):
    reproenv.register_template(template_path)

del template_path, Path
