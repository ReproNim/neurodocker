#!/usr/bin/env python
"""Neurodocker command-line interface to generate Dockerfiles and minify
existing containers.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals
from argparse import Action, ArgumentParser, RawDescriptionHelpFormatter
import logging
import sys

from neurodocker import __version__, Dockerfile, utils
from neurodocker.dockerfile import dockerfile_implementations

logger = logging.getLogger(__name__)

SUPPORTED_SOFTWARE = dockerfile_implementations['software']


# https://stackoverflow.com/a/9028031/5666087
class OrderedArgs(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'ordered_args' in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)


def _add_generate_arguments(parser):
    """Add arguments to `parser` for sub-command `generate`."""
    p = parser
    list_of_kv = lambda kv: kv.split("=")

    p.add_argument("-b", "--base", required=True,
                            help="Base Docker image. Eg, ubuntu:17.04")
    p.add_argument("-p", "--pkg-manager", required=True,
                            choices=utils.manage_pkgs.keys(),
                            help="Linux package manager.")

    # Arguments that should be ordered.
    p.add_argument('--add', action=OrderedArgs, nargs="+",
                   help=("Add file or directory within build context or a URL"
                         " to Docker container filesystem. Use form"
                         " <src> ... <dest>"))
    p.add_argument('--copy', action=OrderedArgs, nargs="+",
                   help=("Copy file or directory within build context to"
                         " Docker container filesystem. Use form"
                         " <src> ... <dest>"))
    p.add_argument('-i', '--instruction', action=OrderedArgs,
                     help=("Arbitrary Dockerfile instruction. Can be used "
                           "multiple times. Added to end of Dockerfile."))
    p.add_argument('--entrypoint', action=OrderedArgs,
                   help="Entrypoint for the Docker image.")
    p.add_argument('-e', '--env', action=OrderedArgs, nargs="+",
                   help="Environment variables to set in Docker image. Use the "
                        "format KEY=VALUE.", type=list_of_kv)
    p.add_argument('-u', '--user', action=OrderedArgs,
                   help="Set the user. If not set, user is root.")
    p.add_argument('--ports', dest="expose", nargs="+",
                   help="Port(s) to expose.", action=OrderedArgs)

    # Other arguments (no order).
    p.add_argument('-o', '--output', dest="output",
                     help="If specified, save Dockerfile to file with this name.")
    p.add_argument('--no-print-df', dest='no_print_df', action="store_true",
                     help="Do not print the Dockerfile")
    p.add_argument("--no-check-urls", action="store_false", dest="check_urls",
                        help=("Do not verify communication with URLs used in "
                              "the build."))

    _ndeb_servers = ", ".join(SUPPORTED_SOFTWARE['neurodebian'].SERVERS.keys())

    # Software package options.
    pkgs_help = {
        "all": (
            "Install software packages. Each argument takes a list of"
            " key=value pairs. Where applicable, the default installation"
            " behavior is to install by downloading and uncompressing"
            " binaries."),
        "afni": (
            "Install AFNI. Valid keys are version (required). Only the latest"
            " version is supported at this time."),
        "ants": (
            "Install ANTs. Valid keys are version (required), use_binaries"
            " (default true), and git_hash. If use_binaries=true, installs"
            " pre-compiled binaries; if use_binaries=false, builds ANTs from"
            " source. If git_hash is specified, build from source from that"
            " commit."),
        "freesurfer": (
            "Install FreeSurfer. Valid keys are version (required),"
            " license_path (relative path to license), and use_binaries"
            " (default true). A FreeSurfer license is required to run the"
            " software and is not provided by Neurodocker."),
        "fsl": (
            "Install FSL. Valid keys are version (required), use_binaries"
            " (default true) and use_installer."),
        "miniconda": (
            "Install Miniconda. Valid keys are env_name (required),"
            " python_version (required), conda_install, pip_install,"
            " add_to_path (default true) and miniconda_version (defaults to"
            " latest). The options conda_install and pip_install accept"
            ' strings of packages: conda_install="traits numpy".'),
        "mrtrix3": (
            "Install MRtrix3. Valid keys are use_binaries (default true) and"
            " git_hash. If git_hash is specified and use_binaries is false,"
            " will checkout to that commit before building."),
        "neurodebian": (
            "Add NeuroDebian repository and optionally install NeuroDebian"
            " packages. Valid keys are os_codename (required; e.g., 'zesty'),"
            " download_server (required), full (if false, default, use libre"
            " packages), and pkgs (list of packages to install). Valid"
            " download servers are {}.".format(_ndeb_servers)),
        "spm": (
            "Install SPM (and its dependency, Matlab Compiler Runtime). Valid"
            " keys are version and matlab_version."),
    }

    pkgs = p.add_argument_group(title="software package arguments",
                                description=pkgs_help['all'])

    for pkg in SUPPORTED_SOFTWARE.keys():
        flag = "--{}".format(pkg)
        # MRtrix3 does not need any arguments by default.
        nargs = "*" if pkg == "mrtrix3" else "+"
        pkgs.add_argument(flag, dest=pkg, nargs=nargs, action=OrderedArgs,
                          metavar="", type=list_of_kv, help=pkgs_help[pkg])


def _add_reprozip_arguments(parser):
    """Add arguments to `parser` for sub-command `reprozip`."""
    p = parser
    p.add_argument('container',
                        help="Running container in which to trace commands.")
    p.add_argument('commands', nargs='+', help="Command(s) to trace.")
    p.add_argument('--dir', '-d', dest="packfile_save_dir", default=".",
                        help=("Directory in which to save pack file. Default "
                              "is current directory."))


def create_parser():
    """Return command-line argument parser."""
    parser = ArgumentParser(description=__doc__, #add_help=False,
                            formatter_class=RawDescriptionHelpFormatter)

    verbosity_choices = ('debug', 'info', 'warning', 'error', 'critical')
    parser.add_argument("-v", "--verbosity", choices=verbosity_choices)
    parser.add_argument("-V", "--version", action="version",
                        version=('neurodocker version {}'.format(__version__)))

    subparsers = parser.add_subparsers(dest="subparser_name",
                                       title="subcommands",
                                       description="valid subcommands")
    generate_parser = subparsers.add_parser('generate',
                                            help="generate dockerfiles")
    reprozip_parser = subparsers.add_parser('reprozip',
                                            help="reprozip trace commands")

    _add_generate_arguments(generate_parser)
    _add_reprozip_arguments(reprozip_parser)

    # Add verbosity option to both parsers. How can this be done with parents?
    generate_parser.add_argument("-v", "--verbosity", choices=verbosity_choices)
    reprozip_parser.add_argument("-v", "--verbosity", choices=verbosity_choices)

    return parser


def parse_args(args):
    """Return namespace of command-line arguments."""
    parser = create_parser()
    return parser.parse_args(args)


def generate(namespace):
    """Run `neurodocker generate`."""
    specs = utils._namespace_to_specs(namespace)
    df = Dockerfile(specs)
    if not namespace.no_print_df:
        print(df.cmd)
    if namespace.output:
        df.save(namespace.output)


def reprozip(namespace):
    """Run `neurodocker reprozip`."""
    from neurodocker.interfaces.reprozip import ReproZip

    local_packfile_path = ReproZip(**vars(namespace)).run()
    logger.info("Saved pack file on the local host:\n{}"
                "".format(local_packfile_path))


def main(args=None):
    """Main program function."""
    if args is None:
        namespace = parse_args(sys.argv[1:])
    else:
        namespace = parse_args(args)

    if namespace.verbosity is not None:
        utils.set_log_level(logger, namespace.verbosity)

    logger.debug(vars(namespace))

    subparser_functions = {'generate': generate,
                           'reprozip': reprozip,}

    if namespace.subparser_name not in subparser_functions.keys():
        print(__doc__)
        return

    subparser_functions[namespace.subparser_name](namespace)


if __name__ == "__main__":  # pragma: no cover
    main()
