import argparse
from distutils.version import LooseVersion

LATEST_PYTHON = "3.6.0"

def get_docker_args():

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


def indent(docker_cmd, text, char=' '):
    """docstring"""
    amount = len(docker_cmd) + 1
    indent = char * amount
    split_lines = text.splitlines(True)

    first_line = "{} {}".format(docker_cmd, split_lines[0])

    if len(split_lines) == 1:
        return first_line

    indented = ''.join(indent+line for line in split_lines[1:])
    return "{}{}".format(first_line, indented)


def install_miniconda(py_version, miniconda_version='latest'):
    """"""
    comment = "# Install miniconda."
    base_url = "https://repo.continuum.io/miniconda/"
    install_file = "Miniconda{}-{}-Linux-x86_64.sh".format(py_version[0], miniconda_version)
    install_url = base_url + install_file

    install_cmd = ("curl -sSLO {install_url} && \\\n"
                   "/bin/bash {install_file} -b -p /usr/local/miniconda && \\\n"
                   "rm {install_file}"
                   "".format(install_url=install_url,
                             install_file=install_file))
    # Add Docker RUN command and indent lines.
    install_cmd = indent("RUN", install_cmd)

    env_cmd = ("PATH=/usr/local/miniconda/bin:$PATH \\\n"
               "PYTHONPATH=/usr/local/miniconda/lib/python{}/site-packages \\\n"
               "PYTHONNOUSERSITE=1 \\\n"
               "LANG=C.UTF-8 \\\n"
               "LC_ALL=C.UTF-8"
               "".format(py_version[:3]))
    # Add Docker command ENV and indent lines.
    env_cmd = indent("ENV", env_cmd)

    conda_env_cmd = ("conda install python={py_version}"
                     "".format(py_version=py_version))
    conda_env_cmd = indent("RUN", conda_env_cmd)

    return "{}\n{}\n{}\n{}".format(comment, install_cmd, env_cmd, conda_env_cmd)


# Only run this if at least one python package is requested.
def install_conda_pkgs(py_packages):
    """Install conda packages. Should list of tuples be param?"""
    comment = "# Install conda packages."

    conda_install_list = []
    for item in py_packages:
        if isinstance(item, tuple):
            # e.g., numpy==1.10
            install_str = "{}=={}".format(item[0], item[1])
            conda_install_list.append(install_str)
        elif isinstance(item, str):
            # e.g., numpy
            conda_install_list.append(item)

    add_channel_cmd = "conda config --add channels conda-forge && \\"
    install_cmd = "conda install -y " + ' '.join(conda_install_list)

    cmd = "{}\n{}".format(add_channel_cmd, install_cmd)
    cmd = indent("RUN", cmd)

    return "{}\n{}".format(comment, cmd)


def concat_docker_cmds(*args):
    """"""
    return '\n\n'.join(args)


def save_dockerfile(fname, info):
    """"""
    with open(fname, 'w') as fp:
        fp.write(info)


def main():
    software = get_docker_args()

    base_img_cmd = "FROM {}".format(software['base'])
    install_miniconda_cmd = install_miniconda(software['py_version'])
    install_conda_pkgs_cmd = install_conda_pkgs(software['py_packages'])

    workdir = "WORKDIR /root"
    reqs = ("apt-get update && apt-get install -y \\\n"
            "curl \\\n"
            "bzip2")
    reqs = indent("RUN", reqs)
    dockerfile = concat_docker_cmds(base_img_cmd,
                                    workdir,
                                    reqs,
                                    install_miniconda_cmd,
                                    install_conda_pkgs_cmd,
                                   )

    save_dockerfile("Dockerfile", dockerfile)

if __name__ == "__main__":
    main()
