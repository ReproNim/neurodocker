#!/usr/bin/env python
"""Command-line utility to generate Dockerfiles, build Docker images, run
commands within containers, and get command ouptut.

Example:

    neurodocker -b ubuntu:17.04 -p apt \
    --ants version=2.1.0 \
    --fsl version=5.0.10 \
    --miniconda python_version=3.5.1 \
                conda_install=traits,pandas \
                pip_install=nipype \
    --spm version=12 matlab_version=R2017a
"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

from neurodocker import (Dockerfile, SpecsParser, SUPPORTED_SOFTWARE)


def create_parser():
    """Return command-line argument parser."""
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)

    # Global requirements.
    reqs = parser.add_argument_group(title="global requirements")
    reqs.add_argument("-b", "--base", required=True,
                      help="Base Docker image. Eg, ubuntu:17.04")
    reqs.add_argument("-p", "--pkg-manager", required=True,
                      help="Linux package manager {apt, yum}")


    # Software package options.
    pkgs_help = {
        "all": ("Install software packages. Each argument takes a list of "
                "key=value pairs.\nWhere applicable, the default installation "
                "behavior is to install by\ndownloading and uncompressing "
                "binaries."),
        "ants": ("Install ANTs. Valid keys are version (required), "
                "use_binaries (default true), and git_hash. If use_binaries="
                "true, installs pre-compiled binaries; if use_binaries=false, "
                "builds ANTs from source. If use_binaries is a URL, download "
                "tarball of ANTs binaries from that URL. If git_hash is "
                "specified, build from source from that commit."),
        "fsl": ("Install FSL. Valid keys are version (required), use_binaries "
                "(default true), use_installer, use_neurodebian, and "
                "os_codename (eg, jessie)."),
        "miniconda": ("Install Miniconda. Valid keys are python_version "
                      "(required), conda_install, pip_install, and "
                      "miniconda_version (defaults to latest). The keys "
                      "conda_install and pip_install take an arbitrary number "
                      "of comma-separated values (no white-space). "
                      "Example: conda_install=pandas,pytest,traits)."),
        "mrtrix3" : ("Install MRtrix3. Valid keys are use_binaries (default "
                     "true) and git_hash. If git_hash is specified and "
                     "use_binaries is false, will checkout to that commit "
                     "before building."),
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


    # Docker-related arguments.
    dkr = parser.add_argument_group(title="Docker-related arguments")
    dkr.add_argument('--no-print-df', dest='no_print_df', action="store_true",
                     help="Do not print the Dockerfile")
    dkr.add_argument('-o', '--output', dest="output",
                     help="If specified, save Dockerfile to file with this name.")
    # dkr.add_argument('--build', dest="build", action="store_true")


    # Other arguments.
    parser.add_argument("--check-urls", dest="check_urls", action="store_true",
                        help=("Verify communication with URLs used in "
                              "the build."), default=True,)
    parser.add_argument("--no-check-urls", action="store_false", dest="check_urls",
                        help=("Do not verify communication with URLs used in "
                              "the build."))
    parser.add_argument("--verbose", action="store_true")

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

    def _list_to_dict(list_of_kv):
        """Convert list of [key, value] pairs to a dictionary."""
        # Flatten list.
        if list_of_kv is not None:
            list_of_kv = [item for sublist in list_of_kv for item in sublist]

            for kv_pair in list_of_kv:
                if len(kv_pair) != 2:
                    raise ValueError("Error in arguments '{}'. Did you forget "
                                     "the equals sign?".format(kv_pair[0]))
                if not kv_pair[-1]:
                    raise ValueError("Option required for '{}'".format(kv_pair[0]))

            return {k: v for k, v in list_of_kv}

    specs = vars(deepcopy(namespace))

    for pkg in SUPPORTED_SOFTWARE.keys():
        specs[pkg] = _list_to_dict(specs[pkg])

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


def main(args=None):

    if args is None:
        namespace = parse_args(sys.argv[1:])
    else:
        namespace = parse_args(args)

    # Create dictionary of specifications.
    specs = convert_args_to_specs(namespace)
    keys_to_remove = ['verbose', 'no_print_df', 'output', 'build']
    for key in keys_to_remove:
        specs.pop(key, None)

    # Parse to double-check that keys are correct.
    parser = SpecsParser(specs)

    # Generate Dockerfile.
    df = Dockerfile(parser.specs)
    if not namespace.no_print_df:
        print(df.cmd)

    if namespace.output:
        df.save(namespace.output)


if __name__ == "__main__":  # pragma: no cover
    main()
