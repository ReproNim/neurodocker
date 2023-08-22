import click

from neurodocker import __version__
from neurodocker.cli.generate import generate, genfromjson


@click.group()
@click.version_option(__version__, message="%(prog)s version %(version)s")
def cli():
    """Generate custom containers, and minify existing containers."""


cli.add_command(generate)
cli.add_command(genfromjson)


def _arm_on_mac() -> bool:
    """Return True if on an ARM processor (M1/M2) in macos operating system."""
    import platform

    is_mac = platform.system().lower() == "darwin"
    is_arm = platform.processor().lower() == "arm"
    return is_mac and is_arm


# If dockerpy is installed, the Docker client can be instantiated, and if we are not
# running on an ARM-based mac computer, then we add the minification command.
# See https://github.com/docker/for-mac/issues/5191 for more information about why
# we skip ARM-based macs.
#
# `docker-py` is required for minification but is not installed by default.
# We also pass if there is an error retrieving the Docker client.
# Say, for example, the Docker engine is not running (or it is not installed).
try:
    from neurodocker.cli.minify.trace import minify

    if not _arm_on_mac():
        cli.add_command(minify)
except (ImportError, RuntimeError):
    # TODO: should we log a debug message? We don't even have a logger at the
    # time of writing, so probably not.
    pass
