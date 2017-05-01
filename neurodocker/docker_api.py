"""Classes to interact with the Docker Engine (using the docker-py package)."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import absolute_import, division, print_function
import posixpath
import threading

import docker
import requests

from neurodocker import SUPPORTED_SOFTWARE
from neurodocker.interfaces import Miniconda
from neurodocker.utils import indent, manage_pkgs


def docker_is_running(client):
    """Return true if Docker server is responsive.

    Parameters
    ----------
    client : docker.client.DockerClient
        The Docker client. E.g., `client = docker.from_env()`.

    Returns
    -------
    running : bool
        True if Docker server is responsive.
    """
    try:
        client.ping()
        return True
    except (requests.exceptions.ConnectionError, docker.errors.APIError):
        return False


# Check whether Docker server is running.
client = docker.from_env()
DOCKER_RUNNING = docker_is_running(client)


def require_docker(func):
    """Raise Exception if Docker server is unresponsive (Docker might not be
    installed or not running). Decorate any function that requires the Docker
    application with this wrapper.

    Parameters
    ----------
    func : callable
        Function that requires Docker to run.

    Returns
    -------
    wrapper : callable
        Wrapped function.
    """
    def wrapper(*args, **kwargs):
        if not DOCKER_RUNNING:
            raise Exception("The Docker server is unresponsive. Is Docker "
                            "installed and running?")
        return func(*args, **kwargs)
    return wrapper


class Dockerfile(object):
    """Class to create Dockerfile.

    Parameters
    ----------
    specs : dict
        Dictionary with keys 'base', etc.
    pkg_manager : {'apt', 'yum'}
        Linux package manager. If None, uses the value of `specs['pkg_manager']`.
    check_urls : bool
        If true, throw warning if a URL used by this class responds with a
        status code greater than 400.
    """

    def __init__(self, specs, pkg_manager=None, check_urls=True):
        self.specs = specs
        self.pkg_manager = pkg_manager
        self.check_urls = check_urls

        if self.pkg_manager is None:
            self.pkg_manager = self.specs['pkg_manager']

        self.cmd = self._create_cmd()

    def __repr__(self):
        return "{self.__class__.__name__}({self.cmd})".format(self=self)

    def __str__(self):
        return self.cmd

    def _create_cmd(self):
        cmds = [self.add_base()]
        if 'debian' in self.specs['base'] or 'ubuntu' in self.specs['base']:
            cmds.append("ARG DEBIAN_FRONTEND=noninteractive")
        cmds.append(self.add_common_dependencies())
        # Install Miniconda before other software.
        if "miniconda" in self.specs.keys():
            cmds.append(self.add_miniconda())
        cmds.append(self.add_software())
        return "\n\n".join(cmds)

    def add_base(self):
        """Add Dockerfile FROM instruction."""
        return "FROM {}".format(self.specs['base'])

    def add_common_dependencies(self):
        """Add Dockerfile instructions to download dependencies common to many
        software packages.
        """
        deps = "bzip2 ca-certificates curl unzip"
        comment = ("#----------------------------\n"
                   "# Install common dependencies\n"
                   "#----------------------------")
        cmd = "{install}\n&& {clean}".format(**manage_pkgs[self.pkg_manager])
        cmd = cmd.format(pkgs=deps)
        cmd = indent("RUN", cmd)
        return "\n".join((comment, cmd))

    def add_miniconda(self):
        """Add Dockerfile instructions to install Miniconda."""
        kwargs = self.specs['miniconda']
        obj = Miniconda(pkg_manager=self.pkg_manager,
                        check_urls=self.check_urls, **kwargs)
        return obj.cmd

    def add_software(self):
        """Add Dockerfile instructions to install neuroimaging software."""
        cmds = []
        for pkg, kwargs in self.specs.items():
            if pkg == 'miniconda':
                continue
            try:
                obj = SUPPORTED_SOFTWARE[pkg](pkg_manager=self.pkg_manager,
                                              check_urls=self.check_urls,
                                              **kwargs)
                cmds.append(obj.cmd)
            except KeyError:
                pass
        return "\n\n".join(cmds)

    def save(self, filepath="Dockerfile", **kwargs):
        """Save `self.cmd` to `filepath`. `kwargs` are for `open()`."""
        if not self.cmd:
            raise Exception("Instructions are empty.")
        with open(filepath, mode='w', **kwargs) as fp:
            fp.write(self.cmd)
            fp.write('\n')


class RawOutputLogger(threading.Thread):
    """Log raw output of Docker commands in separate thread.

    The low-level docker-py API must be used to get raw build logs. Those logs
    are very useful, but they must be combed manually for build errors and
    the ID of the built image.

    For example:
    >>> output = client.api.build(path='path/to/context', rm=True)
    >>> build_logger = RawOutputLogger(output, name="Build-Logger")
    >>> build_logger.daemon = True
    >>> build_logger.start()

    Parameters
    ----------
    generator : generator
        Generator of Docker logs.
    console : bool
        If true, log to console.
    filepath : str
        Log to file `filepath`.
    """
    def __init__(self, generator, console=True, filepath=None, **kwargs):
        self.generator = generator
        self.logger = self.create_logger(console, filepath)
        self.logs = []
        super(RawOutputLogger, self).__init__(**kwargs)

    @staticmethod
    def create_logger(console=True, filepath=None):
        """`console` is bool. If `filepath` is specified, saves logs to file."""
        import logging
        logger = logging.getLogger("build")
        logger.setLevel(logging.DEBUG)
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            logger.addHandler(ch)
        if filepath is not None:
            fh = logging.FileHandler(filepath)
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
        return logger

    def run(self):
        for line in self.generator:
            line = line.decode('utf-8')
            self.logger.debug(line)
            self.logs.append(line)
        self.id = self._get_id()

    def _get_id(self):
        """Get ID of built image or container."""
        import re

        if re.search("successfully built", self.logs[-1], re.IGNORECASE):
            try:
                return re.findall('[0-9a-f]{12}', self.logs[-1])[-1]
            except IndexError:
                return None
        else:
            return None


class DockerImage(object):
    """Build Docker image."""
    def __init__(self, path=None, fileobj=None, tag=None):
        self.path = path
        self.fileobj = fileobj
        self.tag = tag

        try:
            from io import BytesIO
            self.fileobj = BytesIO(self.fileobj.encode('utf-8'))
        except (AttributeError, TypeError):
            pass

        if self.path is None and self.fileobj is None:
            raise ValueError("`path` or `fileobj` must be specified.")

    @require_docker
    def build(self, **kwargs):
        """Return image object."""
        return client.images.build(path=self.path, fileobj=self.fileobj,
                                   tag=self.tag, rm=True, **kwargs)

    @require_docker
    def build_raw(self, console=True, filepath=None, **kwargs):
        """Return generator of raw console output."""
        logs = client.api.build(path=self.path, fileobj=self.fileobj,
                                tag=self.tag, rm=True, **kwargs)
        # QUESTION: how do we prevent multiple threads?
        build_logger = RawOutputLogger(logs, console, filepath,
                                       name="BuildLogger")
        build_logger.daemon = True
        build_logger.start()
        while build_logger.is_alive():
            pass

        try:
            return client.images.get(build_logger.id)
        except docker.errors.NullResource:
            error_logs = build_logger.logs[-2:]
            raise docker.errors.BuildError(error_logs)


class DockerContainer(object):
    def __init__(self, image):
        self.image = image
        self.container = None

    @require_docker
    def start(self, **kwargs):
        """Start the container, and optionally mount volumes. `kwargs` are
        arguments for `client.containers.run()`.

        Equivalent to `docker run -it -d IMAGE`.
        """
        self.container = client.containers.run(self.image, command=None,
                                               detach=True, tty=True,
                                               stdin_open=True, **kwargs)
        return self

    @require_docker
    def exec_run(self, cmd, **kwargs):
        """Execute command inside the container. `kwargs` are arguments for
        `container.exec_run()`.

        Equivalent to `docker exec CONTAINER CMD`.

        Parameters
        ----------
        cmd : str or list
            Command to execute.

        Returns
        -------
        output : str or generator
            If `stream` is false, return output of the command as one string.
            If `stream` is true, return generator of command output.
        """
        output = self.container.exec_run(cmd, **kwargs)
        return output.decode('utf-8')

    def cleanup(self, remove=True, **kwargs):
        """Remove the container. Use `force=True` to remove running container.
        """
        # self.container.stop() --> self.container.remove() would be ideal,
        # but .stop() complains about timing out (even though it stopped the
        # container).
        if remove:
            self.container.remove(**kwargs)
        else:
            self.container.kill(**kwargs)
