"""ReproEnv is a generic generator of Dockerfiles and Singularity files. It forms the
core of Neurodocker.
"""

from neurodocker.reproenv.renderers import DockerRenderer  # noqa: F401
from neurodocker.reproenv.renderers import SingularityRenderer  # noqa: F401
from neurodocker.reproenv.state import register_template  # noqa: F401
from neurodocker.reproenv.state import registered_templates  # noqa: F401
from neurodocker.reproenv.state import get_template  # noqa: F401
from neurodocker.reproenv.template import Template  # noqa: F401
