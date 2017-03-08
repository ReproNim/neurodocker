"""Class to generate Dockerfile."""
from __future__ import absolute_import, division, print_function
import os

from .fsl import FSL
from .miniconda import Miniconda
from .utils import indent
from ..utils import logger


def _append_nonempty(deps_list, items):
    """Append `items` to `deps_list` if `items` is not empty. Operates in-place
    on `deps_list`.
    """
    if items:
        deps_list.append(items)



class Dockerfile(object):
    """Class to generate Dockerfile.

    Parameters
    ----------
    specs : dict
        Software specifications for the Dockerfile.
    savedir : str
        Directory in which to save Dockerfile (and optionally Conda environment
        YAML file).
    deps_method : {'apt-get', 'yum'}
        Method to use to get dependencies.
    """
    def __init__(self, specs, savedir, deps_method):
        self.specs = specs
        self.savedir = savedir
        self._cmds = []

        self._add_base()
        self._get_instructs_and_deps(deps_method)
        self.cmd = "\n\n".join(self._cmds)

    def add_instruction(self, instruction):
        """Add instruction to list of instructions."""
        self._cmds.append(instruction)

    def _add_base(self):
        """Add FROM instruction using specs['base']."""
        cmd = "FROM {}".format(self.specs['base'])
        self.add_instruction(cmd)

    def _get_instructs_and_deps(self, method):
        """Get installation instructions and dependencies of other environment
        specifications while, and remove duplicate dependencies.

        This function will probably become too complicated. Separate getting
        the dependencies and getting the installation instructions.

        Parameters
        ----------
        method : {'apt-get', 'yum'}
            Method to use to get dependencies.
        """
        # Join all dependencies.
        all_deps = []
        all_install_cmds = []
        if 'conda-env' in self.specs:
            miniconda = Miniconda(self.specs['conda-env'],
                                  filepath=self.savedir)
            deps = miniconda.dependencies[method]
            miniconda._save_conda_env()  # Save conda-env.yml file
            _append_nonempty(all_install_cmds, miniconda.cmd)
            _append_nonempty(all_deps, deps)

        # Take care of installation isntructions.
        all_install_cmds = "\n\n".join(all_install_cmds)

        # Take care of dependencies.
        all_deps = [d for sublist in all_deps for d in sublist]  # Flatten list.
        all_deps = set(all_deps)  # Remove duplicates.
        all_deps = sorted(list(all_deps))  # Sort list.
        all_deps = "\n".join(all_deps)  # Join deps into a single string.

        if method == "apt-get":
            cmd = ("apt-get update && apt-get install -y "
                   "--no-install-recommends\n{}".format(all_deps))
        elif method == "yum":
            cmd = ("yum check-update && yum install -y\n{}".format(all_deps))
        install_deps_cmd = indent("RUN", cmd, line_suffix=" \\")
        comment = "# Get dependencies."
        install_deps_cmd = "\n".join((comment, install_deps_cmd))

        self.add_instruction(install_deps_cmd)
        self.add_instruction(all_install_cmds)

    def save(self):
        """Save Dockerfile. Will overwrite file if it exists.

        Parameters
        ----------
        obj : str
            String representation of Dockerfile.
        """
        try:
            filepath = os.path.join(self.savedir, "Dockerfile")
            with open(filepath, 'w') as stream:
                stream.write(self.cmd)
        except NameError:
            raise Exception("Command is not defined yet.")
