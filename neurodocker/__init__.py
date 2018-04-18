import sys

from neurodocker.version import __version__
from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.utils import set_log_level

if sys.version_info[0] < 3:
    raise RuntimeError(
        "Neurodocker requires Python 3. Use Neurodocker's Docker image or"
        " install Python 3.")

set_log_level('info')
