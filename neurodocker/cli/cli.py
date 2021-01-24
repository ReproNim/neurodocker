import click

from neurodocker import __version__
from neurodocker.cli.generate import generate


@click.group()
@click.version_option(__version__, message="%(prog)s version %(version)s")
def cli():
    """Generate custom containers, and minify existing containers."""


cli.add_command(generate)

# `docker-py` is required for minification but is not installed by default.
try:
    from neurodocker.cli.minify.trace import minify

    cli.add_command(minify)
except ImportError:
    pass
