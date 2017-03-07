"""File docstring."""
from __future__ import absolute_import, print_function
import argparse
import os.path as op


def get_docker_args():
    """Return command-line arguments as dictionary."""

    def pypacks(arg):
        """Python package argparse type-checker. If valid arg, return string
        (if no version is specified) or a tuple of (package, version).
        """
        # TODO: the try-except block will not catch errors like "numpy 1.12:".
        # Checks should be more thorough.
        if ':' not in arg:  # assume latest
            return arg
        try:
            package, version = arg.split(':')
            return package, version
        except:
            error = ("Not a valid format. Packages can be specified by either "
                     "`package_name` or `package_name:version`.")
            raise argparse.ArgumentTypeError(error)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-base', required=True,
                        help="The base image to build the docker file from.")
    parser.add_argument('-py', dest='py_version',
                        help="If used, install specific version of Python")
    parser.add_argument('-pp', dest='py_pkgs', type=pypacks, nargs="+",
                        help="Can specify {PACKAGE:VERSION} or just {PACKAGE}")
    args = parser.parse_args()
    return vars(args)


def main():
    env = get_docker_args()

    # Change this so it is not hard-coded.
    d = Dockerfile(env, 'test_out', path='samples/test_out')
    d._save()  # Save Dockerfile.

    # Build image using saved Dockerfile.
    # image = d.build()

    # Run script within Docker container?

if __name__ == "__main__":
    main()
