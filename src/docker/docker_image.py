from __future__ import absolute_import, division, print_function
import os
import posixpath
import threading
import warnings

import docker
import requests

from ..utils import logger


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
    logs : generator
        Generator of Docker logs. Returned by docker.APIClient.events().
    console : bool
        If true, log to console.
    filepath : str
        Log to file `filepath`.
    """
    def __init__(self, logs, console=True, filepath=None, **kwargs):
        self.logs = logs
        self.logger = self.create_logger(console, filepath)
        self.list_of_logs = []
        super(RawOutputLogger, self).__init__(**kwargs)

    @staticmethod
    def create_logger(console=True, filepath=None):
        """`console` is bool. If `filepath` is specified, saves logs to
        file.
        """
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
        for line in self.logs:
            line = line.decode('utf-8')
            self.logger.debug(line)
            self.list_of_logs.append(line)
        self.id = self.get_id()

    def get_id(self):
        """Get ID of built image or container."""
        import re
        last_line = self.list_of_logs[-1]
        if re.search("error", last_line, re.IGNORECASE):
            return None
        elif re.search("successfully built", last_line, re.IGNORECASE):
            return re.search('[0-9a-f]{12}', last_line).group(0)

    def show_logs(self, first=None, last=None):
        """Options `first` and `last` can be integers."""
        if first is not None and last is not None:
            raise ValueError("Options `first` and `last` cannot both be used.")
        elif first is not None:
            return "\n".join(self.list_of_logs[:first])
        elif last is not None:
            return "\n".join(self.list_of_logs[-last:])
        else:
            return "\n".join(self.list_of_logs)


class DockerImage(object):
    """Build Docker image."""
    def __init__(self, path, fileobj=None, tag=None):
        self.path = os.path.abspath(path)
        self.fileobj = None
        self.tag = tag

    @require_docker
    def build(self, **kwargs):
        """Return image object."""
        return client.images.build(path=self.path, fileobj=self.fileobj,
                                   tag=self.tags, **kwargs)

    @require_docker
    def build_raw(self, console=True, filepath=None, **kwargs):
        """Return generator of raw console output."""
        logs = client.api.build(path=self.path, fileobj=self.fileobj,
                                tag=self.tag, **kwargs)
        # QUESTION: how do we prevent multiple threads?
        build_logger = RawOutputLogger(logs, console, filepath,
                                       name="BuildLogger")
        build_logger.daemon = True
        build_logger.start()

        # QUESTION: Is it OK to block here? How else could we do this?
        # Wait for build to finish.
        while build_logger.is_alive():
            pass

        try:
            return client.images.get(build_logger.id)
        except docker.errors.NullResource:
            error_logs = build_logger.show_logs(last=2)
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

    def save_archive(self, path_in_container, filepath):
        """Save a tarball of a file or folder within the Docker container to
        the local machine.

        Parameters
        ----------
        path_in_container : str
            Absolute path to file or folder in the container.
        filepath : str
            Path and name of saved tarball.
        """
        if not posixpath.isabs(path_in_container):
            raise ValueError("`path_in_container` must be absolute.")

        archive = self.container.get_archive(path_in_container)
        response, stat = archive

        with open(filepath, 'wb') as fp:
            fp.write(response.data)
