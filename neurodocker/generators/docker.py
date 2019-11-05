""""""

import copy
import inspect
import json
import logging
import os

from neurodocker.generators.common import _add_to_entrypoint
from neurodocker.generators.common import _get_json_spec_str
from neurodocker.generators.common import _installation_implementations
from neurodocker.generators.common import _install
from neurodocker.generators.common import _Users
from neurodocker.generators.common import ContainerSpecGenerator

logger = logging.getLogger(__name__)


def _indent(string, indent=4, add_list_op=False):
    out = []
    lines = string.splitlines()

    for ii, line in enumerate(lines):
        line = line.rstrip()
        already_cont = line.startswith(('&&', '&', '||', '|', 'fi'))
        previous_cont = (lines[ii - 1].endswith('\\')
                         or lines[ii - 1].startswith('if'))
        if ii:
            if add_list_op and not already_cont and not previous_cont:
                line = "&& " + line
            if not already_cont and previous_cont:
                line = " " * (indent + 3) + line
            else:
                line = " " * indent + line
        if ii != len(lines) - 1:
            if not line.endswith('\\'):
                line += " \\"
        out.append(line)
    return "\n".join(out)


def _dockerfile_base_add_copy(list_srcs_dest, cmd):
    """Base method for `ADD` and `COPY` instructions."""
    if len(list_srcs_dest) < 2:
        raise ValueError("At least two paths must be provided.")

    srcs = list_srcs_dest[:-1]
    dest = list_srcs_dest[-1]

    for src in srcs:
        if os.path.isabs(src):
            raise ValueError("Path for {} cannot be absolute: {}"
                             "".format(cmd, src))
    srcs = '", "'.join(srcs)
    return '{} ["{}", "{}"]'.format(cmd, srcs, dest)


class _DockerfileImplementations:
    @staticmethod
    def add(list_srcs_dest):
        """Return Dockerfile ADD instruction to add file or directory to Docker
        image.

        See https://docs.docker.com/engine/reference/builder/#add.

        Parameters
        ----------
        list_srcs_dest : list of str
            All of the items except the last one are paths on local machine or
            a URL to a file to be copied into the Docker container. Paths on
            the local machine must be within the build context. The last item
            is the destination in the Docker image for these file or
            directories.
        """
        return _dockerfile_base_add_copy(list_srcs_dest, "ADD")

    @staticmethod
    def add_to_entrypoint(cmd):
        """Add command `cmd` to container entrypoint file."""
        return _indent("RUN " + _add_to_entrypoint(cmd))

    @staticmethod
    def arg(arg_dict):
        """Return Dockerfile ARG instruction.

        Parameters
        ----------
        arg_dict : dict
            ARG variables where keys are the variable names, and values are the
            values assigned to those variables.
        """
        cmds = []
        base = "ARG {}"
        for arg, value in arg_dict.items():
            out = base.format(arg)
            if value:  # default value provided.
                value = json.dumps(value)
                out += "={}".format(value)
            cmds.append(out)
        return "\n".join(cmds)

    @staticmethod
    def base(base):
        """Return Dockerfile FROM instruction to specify base image.

        Parameters
        ----------
        base : str
            Base image.
        """
        return "FROM {}".format(base)

    @staticmethod
    def cmd(cmd):
        """Return Dockerfile CMD instruction."""
        escaped = json.dumps(cmd)
        return "CMD {}".format(escaped)

    @staticmethod
    def copy(list_srcs_dest):
        """Return Dockerfile COPY instruction to add files or directories to
        Docker image.

        See https://docs.docker.com/engine/reference/builder/#add.

        Parameters
        ----------
        list_srcs_dest : list of str
            All of the items except the last one are paths on local machine to
            be copied into the Docker container. These paths must be within the
            build context. The last item is the destination in the Docker image
            for these file or directories.
        """
        return _dockerfile_base_add_copy(list_srcs_dest, "COPY")

    @staticmethod
    def entrypoint(entrypoint):
        """Return Dockerfile ENTRYPOINT instruction to set image entrypoint.

        Parameters
        ----------
        entrypoint : str
            The entrypoint.
        """
        escaped = json.dumps(entrypoint)
        return "ENTRYPOINT [{}]".format('", "'.join(escaped.split()))

    @staticmethod
    def env(env_vars):
        """Return Dockerfile ENV instruction to set environment variables.

        Parameters
        ----------
        env_vars : dict
            Environment variables where keys are the environment variables
            names, and values are the values assigned to those environment
            variable names.
        """
        out = ""
        for k, v in env_vars.items():
            newline = "\n" if out else ""
            v = json.dumps(v)  # Escape double quotes and other things.
            out += '{}{}={}'.format(newline, k, v)
        return _indent("ENV " + out)

    @staticmethod
    def expose(exposed_ports):
        """Return Dockerfile EXPOSE instruction to expose ports.

        Parameters
        ----------
        exposed_ports : str, list, tuple
            Port(s) in the container to expose.
        """
        if not isinstance(exposed_ports, (list, tuple)):
            exposed_ports = [exposed_ports]
        return "EXPOSE " + " ".join((str(p) for p in exposed_ports))

    @staticmethod
    def install(pkgs, pkg_manager):
        """Return Dockerfile RUN instruction to install system packages."""
        return _indent("RUN " + _install(pkgs, pkg_manager), add_list_op=True)

    @staticmethod
    def label(labels):
        """Return Dockerfile LABEL instruction to set image labels.

        Parameters
        ----------
        labels : dict
            Dictionary of label names and values.
        """
        out = ""
        for k, v in labels.items():
            newline = "\n" if out else ""
            v = json.dumps(v)  # Escape double quotes and other things.
            out += '{}{}={}'.format(newline, k, v)
        return _indent("LABEL " + out, indent=6)

    @staticmethod
    def run(cmd):
        """Return Dockerfile RUN instruction to run `cmd`."""
        return _indent("RUN " + cmd)

    @staticmethod
    def run_bash(cmd):
        """Return bash command in Dockerfile RUN instruction."""
        cmd = "bash -c '{}'".format(cmd)
        return _DockerfileImplementations.run(cmd)

    @staticmethod
    def shell(sh):
        """Return Dockerfile SHELL instruction to set shell."""
        return 'SHELL ["{}", "-c"]'.format(sh)

    @staticmethod
    def user(user):
        """Return Dockerfile instruction to create `user` if he/she does not
        exist and switch to that user.

        Parameters
        ----------
        user : str
            Name of user to create and switch to.
        """
        user_cmd = "USER {}".format(user)
        add_user_cmd = _Users.add(user)
        if add_user_cmd:
            return "RUN " + add_user_cmd + "\n" + user_cmd
        else:
            return user_cmd

    @staticmethod
    def volume(paths):
        """Return Dockerfile VOLUME instruction.

        Parameters
        ----------
        paths : list
            List of paths in the container.
        """
        escaped = json.dumps(" ".join(paths))
        return "VOLUME [{}]".format('", "'.join(escaped.split()))

    @staticmethod
    def workdir(path):
        """Return Dockerfile WORKDIR instruction to set working directory."""
        return "WORKDIR {}".format(path)


class _DockerfileInterfaceFormatter:
    def __init__(self, interface):
        self.run = interface.render_run()
        self.env = interface.render_env()

    def render(self):
        if self.run and self.env is None:
            return self._render_run()
        elif self.env and self.run is None:
            return self._render_run()
        elif self.env and self.run:
            return self._render_env() + '\n' + self._render_run()

    def _render_env(self):
        """Return string of `ENV` instruction given dictionary of environment
        variables.
        """
        out = "\n".join('{}="{}"'.format(k, v) for k, v in self.env.items())
        return "ENV " + _indent(out)

    def _render_run(self):
        """Return string of `RUN` instruction given string of instructions."""
        return "RUN " + _indent(self.run, add_list_op=True)


class Dockerfile(ContainerSpecGenerator):

    _implementations = {
        **_installation_implementations,
        **dict(
            inspect.getmembers(
                _DockerfileImplementations, predicate=inspect.isfunction))
    }

    def __init__(self, specs):
        self._specs = copy.deepcopy(specs)

        self._prep()
        _Users.clear_memory()

        self._rendered = False

    def render(self):
        # Cache the rendered string.
        if not self._rendered:
            self._rendered = self.commented_header + "\n\n".join(
                self._ispecs_to_dockerfile_str())
        return self._rendered

    def _prep(self):
        self._add_json()
        self._add_header()

    def _add_header(self):
        # If ndfreeze is requested, the order of instructions should be:
        # base, arg noninteractive frontend, ndfreeze, header, entrypoint.
        offset = 1 if self._specs['instructions'][1][0] == 'ndfreeze' else 0
        self._specs['instructions'].insert(
            1, ('user', 'root')
        )
        self._specs['instructions'].insert(
            2, ('arg', {
                'DEBIAN_FRONTEND': 'noninteractive'
            }))
        kwds = {'version': 'generic', 'method': 'custom'}
        self._specs['instructions'].insert(3 + offset, ('_header', kwds))
        self._specs['instructions'].insert(
            4 + offset, ('entrypoint', "/neurodocker/startup.sh"))

    def _ispecs_to_dockerfile_str(self):
        pkg_man = self._specs['pkg_manager']
        for item in self._specs['instructions']:
            instruction, params = item
            if instruction in self._implementations.keys():
                impl = self._implementations[instruction]
                if impl in _installation_implementations.values():
                    try:
                        interface = impl(pkg_manager=pkg_man, **params)
                    except Exception as exc:
                        logger.error("Failed to instantiate {}: {}".format(
                            impl, exc))
                        raise
                    yield _DockerfileInterfaceFormatter(interface).render()
                else:
                    if instruction == 'install':
                        yield impl(params, pkg_manager=pkg_man)
                    else:
                        yield impl(params)
            else:
                raise ValueError(
                    "instruction not understood: '{}'".format(instruction))

    def _add_json(self):
        jsonstr = _get_json_spec_str(self._specs)
        self._specs['instructions'].append(('run', jsonstr))
