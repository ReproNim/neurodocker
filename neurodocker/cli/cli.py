import click

from neurodocker import __version__
from neurodocker.cli.generate import generate
from neurodocker.cli.minify.trace import minify


@click.group()
@click.version_option(__version__, message="%(prog)s version %(version)s")
def cli():
    """Generate custom containers, and minify existing containers."""


cli.add_command(generate)
cli.add_command(minify)
