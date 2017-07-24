#!/usr/bin/env python
"""Neurodocker command-line interface to generate Dockerfiles and minify
existing containers.
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
import sys

from neurodocker import (__version__, Dockerfile, SpecsParser,
                         SUPPORTED_SOFTWARE, utils)

logger = logging.getLogger(__name__)


def _add_generate_arguments(parser):
    """Add arguments to `parser` for sub-command `generate`."""
    parser.add_argument("-b", "--base", required=True,
                            help="Base Docker image. Eg, ubuntu:17.04")
    parser.add_argument("-p", "--pkg-manager", required=True,
                            choices=utils.manage_pkgs.keys(),
                            help="Linux package manager.")
    parser.add_argument('-i', '--instruction', action="append",
                     help=("Arbitrary Dockerfile instruction. Can be used "
                           "multiple times. Added to end of Dockerfile."))
    parser.add_argument('--no-print-df', dest='no_print_df', action="store_true",
                     help="Do not print the Dockerfile")
    parser.add_argument('-o', '--output', dest="output",
                     help="If specified, save Dockerfile to file with this name.")

    parser.add_argument("--check-urls", dest="check_urls", action="store_true",
                        help=("Verify communication with URLs used in "
                              "the build."), default=True)
    parser.add_argument("--no-check-urls", action="store_false", dest="check_urls",
                        help=("Do not verify communication with URLs used in "
                              "the build."))

    _ndeb_servers = ", ".join(SUPPORTED_SOFTWARE['neurodebian'].SERVERS.keys())

    # Software package options.
    pkgs_help = {
        "all": ("Install software packages. Each argument takes a list of "
                "key=value pairs. Where applicable, the default installation "
                "behavior is to install by downloading and uncompressing "
                "binaries."),
        "afni": ("Install AFNI. Valid keys are version (required). Only the "
                 "latest version is supported at this time."),
        "ants": ("Install ANTs. Valid keys are version (required), "
                "use_binaries (default true), and git_hash. If use_binaries="
                "true, installs pre-compiled binaries; if use_binaries=false, "
                "builds ANTs from source. If use_binaries is a URL, download "
                "tarball of ANTs binaries from that URL. If git_hash is "
                "specified, build from source from that commit."),
        "freesurfer": ("Install FreeSurfer. Valid keys are version (required),"
                       "license_path (relative path to license), and "
                       "use_binaries (default true). A FreeSurfer license is "
                       "required to run the software and is not provided by "
                       "Neurodocker."),
        "fsl": ("Install FSL. Valid keys are version (required), use_binaries "
                "(default true) and use_installer."),
        "miniconda": ("Install Miniconda. Valid keys are python_version "
                      "(required), conda_install, pip_install, and "
                      "miniconda_version (defaults to latest). The options "
                      "conda_install and pip_install accept strings of "
                      'packages: conda_install="traits numpy".'),
        "mrtrix3": ("Install MRtrix3. Valid keys are use_binaries (default "
                    "true) and git_hash. If git_hash is specified and "
                    "use_binaries is false, will checkout to that commit "
                    "before building."),
        "neurodebian": ("Add NeuroDebian repository and optionally install "
                        "NeuroDebian packages. Valid keys are os_codename "
                        "(required; e.g., 'zesty'), download_server "
                        "(required), full (if false, default, use libre "
                        "packages), and pkgs (list of packages to install). "
                        "Valid download servers are {}."
                        "".format(_ndeb_servers)),
        "spm": ("Install SPM (and its dependency, Matlab Compiler Runtime). "
                "Valid keys are version and matlab_version."),
    }

    pkgs = parser.add_argument_group(title="software package arguments",
                                         description=pkgs_help['all'])
    list_of_kv = lambda kv: kv.split("=")

    for p in SUPPORTED_SOFTWARE.keys():
        flag = "--{}".format(p)
        # MRtrix3 does not need any arguments by default.
        if p == "mrtrix3":
            pkgs.add_argument(flag, dest=p, action="append", nargs="*",
                              metavar="", type=list_of_kv, help=pkgs_help[p])
            continue
        pkgs.add_argument(flag, dest=p, action="append", nargs="+", metavar="",
                          type=list_of_kv, help=pkgs_help[p])


def _add_reprozip_arguments(parser):
    """Add arguments to `parser` for sub-command `reprozip`."""
    parser.add_argument('container',
                        help="Running container in which to trace commands.")
    parser.add_argument('commands', nargs='+', help="Command(s) to trace.")
    parser.add_argument('--dir', '-d', dest="packfile_save_dir", default=".",
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


def convert_args_to_specs(namespace):
    """Convert namespace of command-line arguments to dictionary compatible
    with `neurodocker.parser.SpecsParser`.
    """
    from copy import deepcopy

    specs = vars(deepcopy(namespace))

    for pkg in SUPPORTED_SOFTWARE.keys():
        specs[pkg] = utils._list_to_dict(specs[pkg])
        utils._string_vals_to_bool(specs[pkg])

    try:
        specs['miniconda']['conda_install'] = \
            specs['miniconda']['conda_install'].replace(',', ' ')
    except (KeyError, TypeError):
        pass

    try:
        specs['miniconda']['pip_install'] = \
            specs['miniconda']['pip_install'].replace(',', ' ')
    except (KeyError, TypeError):
        pass

    return specs


def generate(namespace):
    """Run `neurodocker generate`."""
    specs = convert_args_to_specs(namespace)
    keys_to_remove = ['verbosity', 'no_print_df', 'output', 'build',
                      'subparser_name']
    for key in keys_to_remove:
        specs.pop(key, None)


    parser = SpecsParser(specs)
    df = Dockerfile(parser.specs)
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
