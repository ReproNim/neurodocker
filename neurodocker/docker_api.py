"""Classes to interact with the Docker Engine (using the docker-py package)."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import functools
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
    @functools.wraps(func)
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


class BuildOutputLogger(threading.Thread):
    """Log raw output of `docker build` command in separate thread. This class
    is used to capture the output of the build using the generator returned
    by `docker.APIClient.build()`. Because instances of this class are not in
    the main thread, error checking is done in the DockerImage class (so errors
    are raised in the main thread).

    Parameters
    ----------
    generator : generator
        Generator of build logs.
    console : bool
        If true, log to console.
    filepath : str
        Log to file `filepath`. Default is to not log to file.
    """
    def __init__(self, generator, console=True, filepath=None, **kwargs):
        self.generator = generator
        self.logger = self.create_logger(console, filepath)
        self.logs = []
        super(BuildOutputLogger, self).__init__(**kwargs)

    @staticmethod
    def create_logger(console, filepath):
        import logging
        logger = logging.getLogger("docker_image_build_logs")
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
        from docker.utils.json_stream import json_stream

        for line in json_stream(self.generator):
            self.logger.debug(line)
            self.logs.append(line)


class DockerImage(object):
    """Build Docker image."""
    def __init__(self, dockerfile_obj):
        if not isinstance(dockerfile_obj, Dockerfile):
            raise TypeError("`dockerfile_obj` must be an instance of "
                            "`neurodocker.docker_api.Dockerfile`.")

        from io import BytesIO
        self.fileobj = BytesIO(dockerfile_obj.cmd.encode('utf-8'))

    @require_docker
    def build(self, log_console=False, log_filepath=None, **kwargs):
        """Build image, and return it. If specified, log build output.

        See https://docker-py.readthedocs.io/en/stable/images.html.

        Parameters
        ----------
        log_console : bool
            If true, log to console.
        log_filepath : str
            Log to file `filepath`. Default is to not log to file.
        `kwargs` are for `docker.APIClient.build()`.

        Returns
        -------
        image : docker.models.images.Image
            Docker image object.
        """
        build_logs = client.api.build(fileobj=self.fileobj, **kwargs)

        build_logger = BuildOutputLogger(build_logs, log_console, log_filepath,
                                         name='DockerBuildLogger')
        build_logger.daemon = True
        build_logger.start()
        while build_logger.is_alive():
            pass

        self.image = self._get_image(build_logger)
        return self.image

    @require_docker
    def _get_image(self, build_logger_obj):
        """Helper to check for build errors and return image. This method is
        in the DockerImage class so that errors are raised in the main thread.

        This method borrows from the higher-level API of docker-py.
        See https://github.com/docker/docker-py/pull/1581.
        """
        import re
        from docker.errors import BuildError

        if isinstance(build_logger_obj.generator, str):
            return client.images.get(build_logger_obj.generator)
        if not build_logger_obj.logs:
            return BuildError('Unknown')
        for event in build_logger_obj.logs:
            if 'stream' in event:
                match = re.search(r'(Successfully built |sha256:)([0-9a-f]+)',
                                  event.get('stream', ''))
                if match:
                    image_id = match.group(2)
                    return client.images.get(image_id)

        raise BuildError(last_event.get('error') or build_logger_obj.logs[-1])


class DockerContainer(object):
    """Class to interact with Docker container."""

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

    @require_docker
    def cleanup(self, remove=True, force=False):
        """Stop the container, and optionally remove.

        Parameters
        ----------
        remove : bool
            If true, remove container after stopping.
        force : bool
            If true, force remove container.
        """
        filters = {'status': 'running'}
        try:
            self.container.stop()
        except:
            if container.container in client.containers.list(filters=filters):
                raise docker.errors.APIError("Container not stopped properly.")

        if remove:
            self.container.remove(force=force)
