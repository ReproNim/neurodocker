"""Classes to interact with the Docker Engine (using the package docker-py)"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import functools
import os
import threading

import docker
import requests

client = docker.from_env(version='auto', timeout=30)


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
        if not docker_is_running(client):
            raise Exception("The Docker server is unresponsive. Is Docker "
                            "installed and running?")
        return func(*args, **kwargs)
    return wrapper


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
        self.daemon = True

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
    def __init__(self, dockerfile_or_str):
        from io import BytesIO
        try:
            try:
                self.fileobj = BytesIO(
                    dockerfile_or_str.render().encode('utf-8')
                )
            except AttributeError:
                self.fileobj = BytesIO(dockerfile_or_str.encode('utf-8'))
        except AttributeError:
            raise TypeError("`dockerfile_or_str` must be an instance of "
                            "`neurodocker.generators.docker.Dockerfile` or a string.")

    @require_docker
    def build(self, log_console=False, log_filepath=None, rm=True, **kwargs):
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
        build_logs = client.api.build(fileobj=self.fileobj, rm=rm, **kwargs)

        build_logger = BuildOutputLogger(build_logs, log_console, log_filepath,
                                         name='DockerBuildLogger')
        build_logger.daemon = True
        build_logger.start()
        while build_logger.is_alive():
            pass

        self.image = self._get_image(build_logger)
        return self.image

    @staticmethod
    @require_docker
    def _get_image(build_logger_obj):
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

        last_event = build_logger_obj.logs[-1]
        raise BuildError(
            last_event.get('error') or last_event, build_logger_obj.logs
        )


class DockerContainer(object):
    """Class to interact with Docker container."""

    def __init__(self, image):
        self.image = image
        self.container = None

    @require_docker
    def run(self, command, **kwargs):
        """Run command in the container. `kwargs` are arguments for
        `client.containers.run()`.
        """
        return client.containers.run(self.image, command=command, remove=True,
                                     **kwargs)

    @require_docker
    def start(self, **kwargs):
        """Start the container in the background and optionally mount volumes.
        `kwargs` are arguments for `client.containers.run()`.

        Equivalent to `docker run -td IMAGE`.
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
        output = self.container.exec_run(cmd, **kwargs).output
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
        if remove and force:
            self.container.remove(force=force)
            return

        # If user only wants to stop, attempt to stop the container twice.
        try:
            self.container.stop()
        except (docker.errors.APIError, requests.exceptions.ReadTimeout):
            self.container.stop()
            filters = {'status': 'running'}
            if self.container in client.containers.list(filters=filters):
                raise docker.errors.APIError("Container not stopped properly.")

        # If user wants to stop and remove, but not forcefully.
        if remove:
            self.container.remove()


def copy_file_to_container(container, src, dest):
    """Copy `local_filepath` into `container`:`container_path`.

    Parameters
    ----------
    container : str or container object
        Container to which file is copied.
    src : str
        Filepath on the host.
    dest : str
        Directory inside container. Original filename is preserved.

    Returns
    -------
    success : bool
        True if copy was a success. False otherwise.
    """
    # https://gist.github.com/zbyte64/6800eae10ce082bb78f0b7a2cca5cbc2

    from io import BytesIO
    import tarfile

    try:
        container.put_archive
        container = container
    except AttributeError:
        container = client.containers.get(container)

    with BytesIO() as tar_stream:
        with tarfile.TarFile(fileobj=tar_stream, mode='w') as tar:
            filename = os.path.split(src)[-1]
            tar.add(src, arcname=filename, recursive=False)
        tar_stream.seek(0)
        return container.put_archive(dest, tar_stream)


def copy_file_from_container(container, src, dest='.'):
    """Copy file `filepath` from a running Docker `container`, and save it on
    the host to `save_path` with the original filename.

    Parameters
    ----------
    container : str or container object
        Container from which file is copied.
    src : str
        Filepath within container.
    dest : str
        Directory on the host in which to save file.

    Returns
    -------
    local_filepath : str
        Relative path to saved file on the host.
    """
    import tarfile
    import tempfile

    try:
        container.put_archive
        container = container
    except AttributeError:
        container = client.containers.get(container)

    tar_stream, tar_info = container.get_archive(src)
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            for data in tar_stream:
                tmp.write(data)
            tmp.flush()
            with tarfile.TarFile(tmp.name) as tar:
                tar.extractall(path=dest)
        return os.path.join(dest, tar_info['name'])
    except Exception as e:
        raise
    finally:
        tar_stream.close()
