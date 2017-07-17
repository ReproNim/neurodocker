#!/usr/bin/env python
"""Command-line utility to generate Dockerfiles, build Docker images, run
commands within containers, and get command ouptut.

Example:

    neurodocker generate -b ubuntu:17.04 -p apt \\
    --ants version=2.1.0 \\
    --freesurfer version=6.0.0 license_path="./license.txt" \\
    --fsl version=5.0.10 \\
    --miniconda python_version=3.5.1 \\
                conda_install="traits pandas" \\
                pip_install="nipype" \\
    --mrtrix3 use_binaries=false \\
    --spm version=12 matlab_version=R2017a \\
    --neurodebian os_codename=zesty download_server=usa-nh pkgs="dcm2niix" \\
    --instruction='ENTRYPOINT ["entrypoint.sh"]'
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
import sys

from neurodocker import (__version__, Dockerfile, SpecsParser,
                         SUPPORTED_SOFTWARE, utils)

logger = logging.getLogger(__name__)


def create_parser():
    """Return command-line argument parser."""
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest="subparser_name")
    gen_parser = subparsers.add_parser('generate', description=__doc__,
                                       formatter_class=RawDescriptionHelpFormatter)

    description = """
Trace an arbitrary number of commands in a running container using ReproZip,
and save pack file to host.

Example:
    $> cmd1="echo Hello World"
    $> cmd2="antsRegistration --help"
    $> neurodocker reprozip --dir=~/pack_files f101b18bf98c $cmd1 $cmd2
"""

    reprozip_parser = subparsers.add_parser('reprozip', description=description,
                                            formatter_class=RawDescriptionHelpFormatter)

    # Global requirements.
    reqs = gen_parser.add_argument_group(title="global requirements")
    reqs.add_argument("-b", "--base", required=True,
                      help="Base Docker image. Eg, ubuntu:17.04")
    reqs.add_argument("-p", "--pkg-manager", required=True,
                      help="Linux package manager {apt, yum}")

    _neuro_servers = ", ".join(SUPPORTED_SOFTWARE['neurodebian'].SERVERS.keys())

    # Software package options.
    pkgs_help = {
        "all": ("Install software packages. Each argument takes a list of "
                "key=value pairs. Where applicable, the default installation "
                "behavior is to install by downloading and uncompressing "
                "binaries."),
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
                        "".format(_neuro_servers)),
        "spm": ("Install SPM (and its dependency, Matlab Compiler Runtime). "
                "Valid keys are version and matlab_version."),
    }

    pkgs = gen_parser.add_argument_group(title="software package arguments",
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


    # Docker-related arguments.
    other = gen_parser.add_argument_group(title="other options")
    other.add_argument('-i', '--instruction', action="append",
                     help=("Arbitrary Dockerfile instruction. Can be used "
                           "multiple times."))
    other.add_argument('--no-print-df', dest='no_print_df', action="store_true",
                     help="Do not print the Dockerfile")
    other.add_argument('-o', '--output', dest="output",
                     help="If specified, save Dockerfile to file with this name.")
    # other.add_argument('--build', dest="build", action="store_true")


    # ReproZip sub-command
    reprozip_parser = subparsers.add_parser('reprozip', description=description,
                                            formatter_class=RawDescriptionHelpFormatter)
    reprozip_parser.add_argument('container',
                                 help=("Running container in which to trace "
                                       "commands."))
    reprozip_parser.add_argument('commands', nargs='+',
                                 help="Command(s) to trace.")
    reprozip_parser.add_argument('--dir', '-d', default=".",
                                 help=("Directory in which to save pack file. "
                                       "Default is current directory."))


    # Other options.
    gen_parser.add_argument("--check-urls", dest="check_urls", action="store_true",
                        help=("Verify communication with URLs used in "
                              "the build."), default=True)
    gen_parser.add_argument("--no-check-urls", action="store_false", dest="check_urls",
                        help=("Do not verify communication with URLs used in "
                              "the build."))
    verbosity_choices = ('debug', 'info', 'warning', 'error', 'critical')
    parser.add_argument("-v", "--verbosity", choices=verbosity_choices)
    parser.add_argument("-V", "--version", action="version",
                        version=('neurodocker version {version}'
                                 .format(version=__version__)))

    return parser


def parse_args(args):
    """Return namespace of command-line arguments."""
    parser = create_parser()
    return parser.parse_args(args)


def _list_to_dict(list_of_kv):
    """Convert list of [key, value] pairs to a dictionary."""
    if list_of_kv is not None:
        list_of_kv = [item for sublist in list_of_kv for item in sublist]

        for kv_pair in list_of_kv:
            if len(kv_pair) != 2:
                raise ValueError("Error in arguments '{}'. Did you forget "
                                 "the equals sign?".format(kv_pair[0]))
            if not kv_pair[-1]:
                raise ValueError("Option required for '{}'".format(kv_pair[0]))

        return {k: v for k, v in list_of_kv}


def _string_vals_to_bool(dictionary):
    """Convert string values to bool."""
    import re

    bool_vars = ['use_binaries', 'use_installer', 'use_neurodebian']

    if dictionary is None:
        return

    for key in dictionary.keys():
        if key in bool_vars:
            if re.search('false', dictionary[key], re.IGNORECASE):
                dictionary[key] = False
            elif re.search('true', dictionary[key], re.IGNORECASE):
                dictionary[key] = True
            else:
                dictionary[key] = bool(int(dictionary[key]))


def convert_args_to_specs(namespace):
    """Convert namespace of command-line arguments to dictionary compatible
    with `neurodocker.parser.SpecsParser`.
    """
    from copy import deepcopy

    specs = vars(deepcopy(namespace))

    for pkg in SUPPORTED_SOFTWARE.keys():
        specs[pkg] = _list_to_dict(specs[pkg])
        _string_vals_to_bool(specs[pkg])

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

    # Parse to double-check that keys are correct.
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

    subparser_functions = {'generate': generate,
                           'reprozip': reprozip,}

    if namespace.verbosity is not None:
        utils.set_log_level(logger, namespace.verbosity)


    if namespace.subparser_name not in subparser_functions.keys():
        print(__doc__)
        return
    subparser_functions[namespace.subparser_name](namespace)




if __name__ == "__main__":  # pragma: no cover
    main()
