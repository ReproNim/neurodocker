""""""

import datetime
import json
import os
import posixpath

from neurodocker import __version__
from neurodocker.interfaces._base import _BaseInterface
from neurodocker.interfaces._base import apt_install
from neurodocker.interfaces._base import yum_install

_installation_implementations = {
    ii._name: ii
    for ii in _BaseInterface.__subclasses__()
}

ND_DIRECTORY = posixpath.join(posixpath.sep, 'neurodocker')
NEURODOCKER_ENTRYPOINT = posixpath.join(ND_DIRECTORY, 'startup.sh')
SPEC_FILE = posixpath.join(ND_DIRECTORY, 'neurodocker_specs.json')

# TODO: add common methods like `--install` here. Reference them in the
# Dockerfile and SingularityRecipe implementation classes.


def _add_to_entrypoint(cmd):
    """Return command to add `cmd` to the container's entrypoint."""
    base_cmd = "sed -i '$i{}' $ND_ENTRYPOINT"
    escaped_bash_cmd = json.dumps(cmd)[1:-1]
    return base_cmd.format(escaped_bash_cmd)


def _apt_install(pkgs, apt_opts=None):
    if apt_opts is None:
        return apt_install.render(pkgs=pkgs)
    else:
        return apt_install.render(pkgs=pkgs, apt_opts=apt_opts)


def _yum_install(pkgs, yum_opts=None):
    return yum_install.render(pkgs=pkgs, yum_opts=yum_opts)


def _install(pkgs, pkg_manager):
    """Return instructions to install system packages."""
    installers = {
        'apt': _apt_install,
        'yum': _yum_install,
    }
    if pkg_manager not in installers.keys():
        raise ValueError(
            "package manager '{}' not recognized".format(pkg_manager))
    opts_key = "{}_opts=".format(pkg_manager)
    opts = [jj for jj in pkgs if jj.startswith(opts_key)]
    pkgs = [kk for kk in pkgs if kk not in opts]
    opts = opts[0].replace(opts_key, '') if opts else None
    return installers[pkg_manager](pkgs, opts)


class _Users:
    """Object to hold memory of initialized users."""

    initialized_users = {'root'}

    @classmethod
    def add(cls, user):
        """If user has not been created yet, return command to create user.
        Otherwise, return False.
        """
        if user not in cls.initialized_users:
            cls.initialized_users.add(user)
            return (
                # Test whether the user exists. If not, add user.
                'test "$(getent passwd {0})" ||'
                ' useradd --no-user-group --create-home --shell /bin/bash {0}'
                .format(user))
        else:
            return False

    @classmethod
    def clear_memory(cls):
        cls.initialized_users = {'root'}


def _get_json_spec_str(specs):
    """Return instruction to write out specs dictionary to JSON file."""
    js = json.dumps(specs, indent=2)
    js = js.replace('\\n', '__TO_REPLACE_NEWLINE__')
    js = "\n\\n".join(js.split("\n"))
    # Escape newline characters that the user provided.
    js = js.replace('__TO_REPLACE_NEWLINE__', '\\\\n')
    # Workaround to escape single quotes in a single-quoted string.
    # https://stackoverflow.com/a/1250279/5666087
    js = js.replace("'", """'"'"'""")
    cmd = "echo '{string}' > {path}".format(string=js, path=SPEC_FILE)
    return cmd


class ContainerSpecGenerator:
    """Base class for classes that generate container spec files."""

    def render(self):
        raise NotImplementedError("not implemented")

    def save(self, filepath):
        """Save the rendered container specification to a file."""
        if os.path.exists(filepath):
            raise FileExistsError("File already exists: {}".format(filepath))
        rendered = self.render()
        with open(filepath, mode='w') as fp:
            fp.write(rendered + '\n')

    @property
    def commented_header(self):
        t = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
        header = (
            "Timestamp: {time} UTC"
            "\n\n"
            "Thank you for using Neurodocker. If you discover any issues"
            "\nor ways to improve this software, please submit an issue or"
            "\npull request on our GitHub repository:"
            "\n\n    https://github.com/ReproNim/neurodocker")
        header = header.format(version=__version__, time=t)
        return "# " + header.replace("\n", "\n# ") + "\n\n"
