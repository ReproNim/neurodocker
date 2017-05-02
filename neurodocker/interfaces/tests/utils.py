"""Utility functions for `neurodocker.interfaces.tests`."""
from __future__ import absolute_import

from neurodocker import Dockerfile, DockerImage, DockerContainer, SpecsParser
from neurodocker.docker_api import client

def get_container_from_specs(specs, **kwargs):
    """Return started container. `kwargs` are for `container.start()`."""
    parser = SpecsParser(specs)
    df = Dockerfile(parser.specs)
    image = DockerImage(df).build()
    return DockerContainer(image).start(**kwargs)

def test_cleanup(container):
    container.cleanup(remove=True, force=True)
    client.containers.prune()
    client.images.prune()
