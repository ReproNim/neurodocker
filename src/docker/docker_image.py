from __future__ import absolute_import, division, print_function
import os
import posixpath
import threading

import docker

from ..utils import logger


def _create_volumes_dict(volume_mapping):
    """Create dictionary to pass to `volumes` kwarg of `docker.api.build()`.

    >>> volume_mapping = [("local/dir", "/path/on/docker", "rw")]
    >>> create_volumes_dict(volume_mapping)
    {'/abspath/to/local/dir': {'bind': '/path/on/docker',
                               'mode': 'rw'}}

    Parameters
    ----------
    volume_mapping : list
        List of tuples. Items in each tuple specify the directory on the local
        machine, the directory in the docker container to which the local
        directory should be mapped, and the read/write permissions of that
        directory. Read-write permissions can be either "rw" for read/write or
        "ro" for read-only. Permissions will be read-write if not specified.

    Returns
    -------
    volumes : dict
        Dictionary of volumes to be passed to `volumes` kwargs of
        `docker.api.build()`.
    """
    volumes = {}
    for this_volume in volume_mapping:
        try:
            local_path, docker_path, permissions = this_volume
        except ValueError:
            local_path, docker_path = this_volume
            permissions = "rw"

        # There is a chance symbolic links could cause issues with Docker.
        local_path = os.path.realpath(local_path)
        if not posixpath.isabs(docker_path):
            raise ValueError("Path '{}' is not absolute".format(docker_path))
        if permissions not in ['rw', 'ro']:
            raise ValueError("Unrecognized permissions: '{}'"
                             "".format(permissions))

        volumes[local_path] = {"bind": docker_dir, "mode": permissions}

    return volumes


class EventLogger(threading.Thread):
    """Log Docker events in separate thread.

    >>> events = client.events(decode=True)
    >>> event_logger = EventLogger(events, name="Event-Logger", daemon=True)
    >>> event_logger.start()

    Parameters
    ----------
    events : generator
        Generator of Docker logs. Returned by docker.APIClient.events().
    """
    def __init__(self, events, **kwargs):
        self.events = events
        super(EventLogger, self).__init__(**kwargs)

    def run(self):
        for line in self.events:
            try:
                for key in line:
                    logger.debug("{}: {}".format(key, line[key]))
            except:
                logger.debug(line)


class DockerImage(object):
    """Class to build and run Docker image.

    Parameters
    ----------

    """
    client = docker.from_env()
    # Test communication with the Docker daemon. Raises docker.errors.APIError
    # if communication fails.
    client.ping()

    # Log Docker events in separate thread.
    events = client.events(decode=True)
    event_logger = EventLogger(events, name="Event-Logger")
    event_logger.daemon = True
    event_logger.start()

    def __init__(self, path=None, fileobj=None, **kwargs):
        self.path = path
        self.fileobj = fileobj
        # kwargs?

        # Build image. This method uses the higher-level Docker API. To get the
        # raw output (like you would see if using Docker on the command-line),
        # we would have to use the lower-level Docker API. The lower-level
        # build method returns a blocking generator of the raw output, so we
        # would have to figure out how to get the image ID after it is built.
        self.image = DockerImage.client.images.build(path=path,
                                                     fileobj=fileobj,
                                                     rm=True,
                                                     **kwargs)

    def _create_volumes_dict(self, volume_mapping):
        """Create mapping of volumes. See the documentation for the global
        function _create_volumes_dict()."""
        self.volumes = _create_volumes_dict(volume_mapping)
        return self.volumes

    def run(self, command, **kwargs):
        """Run command within Docker container. Blocks until command finishes
        running. Console output of the command can be accessed with the method
        `self.container.logs()`.

        Parameters
        ----------
        command : str
            Command to run within container.
        """
        # The below method will return a container object only if `detach`
        # is true.
        self.container = DockerImage.client.containers.run(self.image,
                                                           command=command,
                                                           detach=True)

    def _get_console_output(self):
        """Return the console output of the `run` method."""
        try:
            # `container.logs()` returns bytes.
            return self.container.logs().decode(encoding='utf-8').strip()
        except NameError:
            raise Exception("Container must be run for there to be output.")
