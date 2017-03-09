from __future__ import absolute_import, division, print_function

import docker

from ..utils import logger



class DockerAPI(object):
    """Class to interact with Docker Engine, via `docker` package.

    Parameters
    ----------

    """
    client = docker.from_env()
    events = client.events(decode=True)
    event_logger = EventLogger(events, name="Event-Logger", daemon=True)
    event_logger.start()

    def __init__(self):
        pass

    def _build_image(self, tag, path=None, fileobj=None, **kwargs):
        """Build Docker image.

        Parameters
        ----------

        Returns
        -------
        image
        """
        # This method uses the higher-level Docker API. To get the raw output
        # (like you would see if using Docker on the command-line), we would
        # have to use the lower-level Docker API.
        self.tag = tag
        self.path = path
        self.fileobj = fileobj

        self.image = client.images.build(path=self.path, fileobj=self.fileobj,
                                         tag=self.tag, rm=True, **kwargs)
        return self.image

    def _create_container(self, **kwargs):
        """Create container from image `self.image`."""
        # kwargs are same as docker.containers.run()
        # use `volumes` kwarg to mount directories.
        try:
            self.container = client.containers.create(self.image, **kwargs)
        except NameError:
            raise Exception("Image must be built before container can be made.")

    def _start_container(self, **kwargs):
        """"""
        self.container.start(**kwargs)

    def _exec_run(self, **kwargs):
        """"""
        self.container._exec_run(**kwargs)

    def _stop_container(self, **kwargs):
        """"""
        self.container.stop(**kwargs)



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
