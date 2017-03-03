import argparse
from distutils.version import LooseVersion

LATEST_PYTHON = "3.6.0"

def main():

    def pypacks(arg):
        """
        Python package argparse type-checker
        If valid arg, returns either as string (if no version is specified)
        or a 2-item tuple
        """
        if ':' not in arg: #assume latest
            return arg
        try:
            package, version = arg.split(':')
            return package, version
        except:
            raise argparse.ArgumentTypeError("Not a valid format."
                            "Packages can be specified by either {PACKAGE_NAME} "
                            "or {PACKAGE_NAME,VERSION}")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-base', required=True,
                        help="The base image to build the docker file from.")
    parser.add_argument('-py', dest='py_version', default=None,
                        help="If used, install specific version of Python")
    parser.add_argument('-pp', dest='py_packages', type=pypacks, nargs="+",
                        help="Can specify {PACKAGE:VERSION} or just {PACKAGE}")
    args = parser.parse_args()
    if args.py_version:
        if LooseVersion(args.py_version) > LooseVersion(LATEST_PYTHON):
            raise Exception("Version of Python is not available yet!")
    return vars(args)

if __name__ == "__main__":
    main()
