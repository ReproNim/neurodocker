import sys

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.utils import set_log_level

if sys.version_info[0] < 3:
    raise RuntimeError(
        "Neurodocker requires Python 3. Use Neurodocker's Docker image or"
        " install Python 3.")

set_log_level('info')
