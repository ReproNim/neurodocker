#!/usr/bin/env python3
"""Neurodocker is a command-line interface to generate custom Dockerfiles and
Singularity recipes.

For help generating Dockerfiles and Singularity recipes, run

$ neurodocker generate docker --help
$ neurodocker generate singularity --help
"""

from argparse import Action
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import json
import logging
import sys

import etelemetry

from neurodocker import __version__
from neurodocker import utils
from neurodocker.generators import Dockerfile
from neurodocker.generators import SingularityRecipe
from neurodocker.generators.common import _installation_implementations

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/9028031/5666087
class OrderedArgs(Action):
    """Object to preserve order in which command-line arguments are given."""

    def __call__(self, parser, namespace, values, option_string=None):
        if 'ordered_args' not in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)


def _list_of_kv(kv):
    """Split string `kv` at first equals sign."""
    ll = kv.split("=")
    ll[1:] = ["=".join(ll[1:])]
    return ll


def _add_generate_common_arguments(parser):
    p = parser

    p.add_argument(
        "-b", "--base", help="Base Docker image. E.g., debian:stretch")
    p.add_argument(
        "-p",
        "--pkg-manager",
        choices={'apt', 'yum'},
        help="Linux package manager.")
    p.add_argument(
        '--add-to-entrypoint',
        action=OrderedArgs,
        help=("Add a command to the file /neurodocker/startup.sh, which is the"
              " container's default entrypoint."))
    p.add_argument(
        '--copy',
        action=OrderedArgs,
        nargs="+",
        help="Copy files into container. Use format <src>... <dest>")
    p.add_argument(
        '--install',
        action=OrderedArgs,
        nargs="+",
        help=("Install system packages with apt-get or yum, depending on the"
              " package manager specified."))
    p.add_argument(
        '--entrypoint',
        action=OrderedArgs,
        help="Set the container's entrypoint (Docker) / append to runscript"
        " (Singularity)")
    p.add_argument(
        '-e',
        '--env',
        action=OrderedArgs,
        nargs="+",
        type=_list_of_kv,
        help="Set environment variable(s). Use the format KEY=VALUE")
    p.add_argument(
        '-r',
        '--run',
        action=OrderedArgs,
        help="Run a command when building container")
    p.add_argument(
        '--run-bash', action=OrderedArgs, help="Run a command in bash")
    p.add_argument(
        '-u',
        '--user',
        action=OrderedArgs,
        help="Switch current user (creates user if necessary)")
    p.add_argument(
        '-w', '--workdir', action=OrderedArgs, help="Set working directory")

    # To generate from file.
    p.add_argument(
        'file',
        nargs='?',
        help="Generate file from JSON. Overrides other `generate` arguments")
    p.add_argument(
        '--json', action="store_true", help="Print Neurodocker JSON spec")

    # Other arguments (no order).
    p.add_argument(
        '-o',
        '--output',
        dest="output",
        help="If specified, save Dockerfile to file with this name.")
    p.add_argument(
        '--no-print',
        dest='no_print',
        action="store_true",
        help="Do not print the generated file")

    _ndeb_servers = ", ".join(
        _installation_implementations['neurodebian']._servers.keys())

    # Software package options.
    pkgs_help = {
        "all":
        "Install software packages. Each argument takes a list of"
        " key=value pairs. Where applicable, the default installation"
        " behavior is to install by downloading and uncompressing"
        " binaries. Some programs can be built from source.",
        "afni":
        "Install AFNI. Valid keys are version (required), method,"
        " install_path, install_r, install_r_pkgs, install_python2,"
        " and install_python3. Only the latest version and version"
        " 17.2.02 are supported at this time.",
        "ants":
        "Install ANTs. Valid keys are version (required), method"
        " install_path, cmake_opts, and make_opts. Version can be a "
        " git commit hash if building from source.",
        "convert3d":
        "Install Convert3D. Valid keys are version (required),"
        " method, and install_path.",
        "dcm2niix":
        "Install dcm2niix. Valid keys are version, method,"
        " install_path, cmake_opts, and make_opts",
        "freesurfer":
        "Install FreeSurfer. Valid keys are version (required),"
        " method, install_path, and exclude_paths. A FreeSurfer"
        " license is required to run the software and is not"
        " provided by Neurodocker.",
        "fsl":
        "Install FSL. Valid keys are version (required), method,"
        " install_path, and exclude_paths.",
        "matlabmcr":
        "Install Matlab Compiler Runtime. Valid keys are version,"
        " method, and install_path",
        "miniconda":
        "Install Miniconda. Valid keys are install_path,"
        " env_name, conda_install, pip_install, conda_opts,"
        " pip_opts, activate (default false), and version"
        " (defaults to latest). The options conda_install and"
        " pip_install accept strings of packages: conda_install="
        '"python=3.6 numpy traits".',
        "mricron":
        "Install MRIcron. valid keys are version (required), method, and"
        " install_path.",
        "mrtrix3":
        "Install MRtrix3. Valid keys are version (required),"
        " method, and install_path",
        "ndfreeze":
        "Use the NeuroDebian command `nd_freeze` to freeze the apt"
        " sources to a certain date. This will only have an effect"
        " on Debian and NeuroDebian APT sources.",
        "neurodebian":
        "Add NeuroDebian repository. Valid keys are "
        "os_codename (e.g., zesty), server (e.g., usa-nh), and"
        " full (if true, use non-free packages). Valid download"
        " servers are {}.".format(_ndeb_servers),
        "spm12":
        "Install SPM12 and its dependency, Matlab Compiler Runtime."
        " Valid keys are version and install_path.",
        "minc":
        "Install MINC. Valid keys is version (required), method, and"
        " install_path. Only version 1.9.15 is supported at this"
        " time.",
        "petpvc":
        "Install PETPVC. Valid keys are version (required), method,"
        " and install_path.",
        "vnc":
        "Install a VNC server. Valid keys are passwd (required),"
        " start_at_runtime, and geometry."
    }

    pkgs = p.add_argument_group(
        title="software package arguments", description=pkgs_help['all'])

    for pkg in _installation_implementations.keys():
        if pkg == '_header':
            continue
        flag = "--{}".format(pkg)
        # MRtrix3 does not need any arguments by default.
        nargs = "*" if pkg == "mrtrix3" else "+"
        pkgs.add_argument(
            flag,
            dest=pkg,
            nargs=nargs,
            action=OrderedArgs,
            metavar="",
            type=_list_of_kv,
            help=pkgs_help[pkg])


def _add_generate_docker_arguments(parser):
    """Add arguments to `parser` for sub-command `generate docker`."""
    p = parser

    # Arguments that should be ordered.
    p.add_argument(
        '--add',
        action=OrderedArgs,
        nargs="+",
        help="Dockerfile ADD instruction. Use format <src>... <dest>")
    p.add_argument(
        '--arg',
        action=OrderedArgs,
        nargs="+",
        type=_list_of_kv,
        help="Dockerfile ARG instruction. Use format KEY[=DEFAULT_VALUE] ...")
    p.add_argument(
        '--cmd',
        action=OrderedArgs,
        nargs="+",
        help="Dockerfile CMD instruction.")
    p.add_argument(
        '--expose',
        nargs="+",
        action=OrderedArgs,
        help="Dockerfile EXPOSE instruction.")
    p.add_argument(
        '--label',
        action=OrderedArgs,
        nargs="+",
        type=_list_of_kv,
        help="Dockerfile LABEL instruction.")
    p.add_argument(
        '--volume',
        action=OrderedArgs,
        nargs="+",
        help="Dockerfile VOLUME instruction.")


def _add_generate_singularity_arguments(parser):
    """Add arguments to `parser` for sub-command `generate singularity`."""
    pass


def _add_reprozip_trace_arguments(parser):
    """Add arguments to `parser` for sub-command `reprozip-trace`."""
    p = parser
    p.add_argument(
        'container', help="Running container in which to trace commands.")
    p.add_argument('commands', nargs='+', help="Command(s) to trace.")
    p.add_argument(
        '--dir',
        '-d',
        dest="packfile_save_dir",
        default=".",
        help=("Directory in which to save pack file. Default "
              "is current directory."))


def _add_reprozip_merge_arguments(parser):
    """Add arguments to `parser` for sub-command `reprozip-merge`."""
    p = parser
    p.add_argument('outfile', help="Filepath to merged pack file.")
    p.add_argument('pack_files', nargs='+', help="Pack files to merge.")


def create_parser():
    """Return command-line argument parser."""

    parser = ArgumentParser(
        description=__doc__, formatter_class=RawDescriptionHelpFormatter)

    verbosity_choices = ('debug', 'info', 'warning', 'error', 'critical')
    parser.add_argument("-v", "--verbosity", choices=verbosity_choices)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=('neurodocker version {}'.format(__version__)))

    subparsers = parser.add_subparsers(
        dest="subparser_name",
        title="subcommands",
        description="valid subcommands")

    # `neurodocker generate` parsers.
    generate_parser = subparsers.add_parser(
        'generate', help="generate recipes")
    generate_subparsers = generate_parser.add_subparsers(
        dest="subsubparser_name",
        title="subcommands",
        description="valid subcommands")
    generate_docker_parser = generate_subparsers.add_parser(
        'docker', help="generate Dockerfile")
    generate_singularity_parser = generate_subparsers.add_parser(
        'singularity', help="generate Singularity recipe")
    _add_generate_common_arguments(generate_docker_parser)
    _add_generate_docker_arguments(generate_docker_parser)
    _add_generate_common_arguments(generate_singularity_parser)
    _add_generate_singularity_arguments(generate_singularity_parser)

    # `neurodocker reprozip` parsers.
    reprozip_parser = subparsers.add_parser('reprozip', help="")
    reprozip_subparsers = reprozip_parser.add_subparsers(
        dest="subsubparser_name",
        title="subcommands",
        description="valid subcommands")
    reprozip_trace_parser = reprozip_subparsers.add_parser(
        'trace', help="minify container for traced command(s)")
    reprozip_merge_parser = reprozip_subparsers.add_parser(
        'merge', help="merge reprozip pack files")
    _add_reprozip_trace_arguments(reprozip_trace_parser)
    _add_reprozip_merge_arguments(reprozip_merge_parser)

    # Add verbosity option to both parsers. How can this be done with parents?
    for p in (generate_parser, reprozip_trace_parser, reprozip_merge_parser):
        p.add_argument("-v", "--verbosity", choices=verbosity_choices)

    return parser


def parse_args(args):
    """Return namespace of command-line arguments."""
    parser = create_parser()
    namespace = parser.parse_args(args)

    if namespace.subparser_name is None:
        parser.print_help()
        parser.exit(1)
    elif (namespace.subparser_name == 'generate'
          and namespace.subsubparser_name is None):
        parser.print_help()
        parser.exit(1)
    elif (namespace.subparser_name == 'reprozip'
          and namespace.subsubparser_name is None):
        parser.print_help()
        parser.exit(1)
    elif (namespace.subparser_name == 'generate'
          and namespace.subsubparser_name in {'docker', 'singularity'}):
        _validate_generate_args(namespace)

    return namespace


def generate(namespace):
    """Run `neurodocker generate`."""
    if namespace.file is None:
        specs = utils._namespace_to_specs(namespace)
    else:
        specs = utils.load_json(namespace.file)

    recipe_objs = {
        'docker': Dockerfile,
        'singularity': SingularityRecipe,
    }

    recipe_obj = recipe_objs[namespace.subsubparser_name](specs)
    if namespace.json:
        print(json.dumps(specs))
    elif not namespace.no_print:
        print(recipe_obj.render())
    if namespace.output:
        recipe_obj.save(filepath=namespace.output)


def reprozip_trace(namespace):
    """Run `neurodocker reprozip`."""
    from neurodocker.reprozip import ReproZipMinimizer

    local_packfile_path = ReproZipMinimizer(**vars(namespace)).run()
    logger.info("Saved pack file on the local host:\n{}"
                "".format(local_packfile_path))


def reprozip_merge(namespace):
    """Run `neurodocker reprozip merge`."""
    from neurodocker.reprozip import merge_pack_files

    merge_pack_files(namespace.outfile, namespace.pack_files)


def _validate_generate_args(namespace):
    if (namespace.file is None
            and (namespace.base is None or namespace.pkg_manager is None)):
        raise ValueError("-b/--base and -p/--pkg-manager are required if not"
                         " generating from JSON file.")


def main(args=None):
    """Main program function."""
    if args is None:
        namespace = parse_args(sys.argv[1:])
    else:
        namespace = parse_args(args)

    if namespace.verbosity is not None:
        utils.set_log_level(namespace.verbosity)

    logger.debug(vars(namespace))


    etelemetry_version = etelemetry.check_available_version(
        "ReproNim/neurodocker", __version__, lgr=logger)

    print("# Generated by: Neurodocker version {}".format(__version__))
    if etelemetry_version and 'version' in etelemetry_version:
        print("# Latest release: Neurodocker version {}".format(
            etelemetry_version["version"]))

    subparser_functions = {
        'docker': generate,
        'singularity': generate,
        'trace': reprozip_trace,
        'merge': reprozip_merge,
    }

    subparser_functions[namespace.subsubparser_name](namespace)


if __name__ == "__main__":  # pragma: no cover
    main()
