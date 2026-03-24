"""Neurodocker generates containers for neuroimaging.

It includes ReproEnv, which is an extensible, generic container generator.
"""

from pathlib import Path

from neurodocker import reproenv
from neurodocker._version import __version__

__version__ = __version__

# Register neurodocker templates
# TODO: remove registration from the `generate` cli. otherwise we register twice.
for template_path in (Path(__file__).parent / "templates").glob("*.yaml"):
    reproenv.register_template(template_path)

del template_path, Path
