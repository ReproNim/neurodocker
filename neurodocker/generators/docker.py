""""""

import inspect
import json
import os

from neurodocker.generators.common import _installation_implementations


def _add_slashes(string):
    """Return string with slashes added to each line."""
    lines = string.strip().splitlines()
    return "\n".join(line if line.endswith('\\') or ii == len(lines) - 1
                     else line + " \\"
                     for ii, line in enumerate(lines))


def _indent(string, indent=4, indent_first_line=False):
    indent = 4
    indent_first_line = False
    separator = " \\\n" + " " * indent
    if not indent_first_line:
        return separator.join(string.splitlines())
    else:
        return " " * indent + separator.join(string.splitlines())


def _dockerfile_base_add_copy(list_srcs_dest, cmd):
    """Base method """
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
        return _indent("LABEL", out)

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
        return "RUN " + _indent(self.run)


class Dockerfile:

    _implementations = {
        **_installation_implementations,
        **dict(inspect.getmembers(_DockerfileImplementations,
               predicate=inspect.isfunction))
    }

    def __init__(self, specs):
        self._specs = specs

    def render(self):
        return "\n\n".join(self._ispecs_to_dockerfile_str())

    def _ispecs_to_dockerfile_str(self):
        pkg_man = self._specs['pkg_manager']
        for item in self._specs['instructions']:
            instruction, params = item
            if instruction in self._implementations.keys():
                impl = self._implementations[instruction]
                if impl in _installation_implementations.values():
                    interface = impl(pkg_manager=pkg_man, **params)
                    yield _DockerfileInterfaceFormatter(interface).render()
                else:
                    yield impl(params)
            else:
                raise ValueError(
                    "instruction not understood: '{}'".format(instruction)
                )
