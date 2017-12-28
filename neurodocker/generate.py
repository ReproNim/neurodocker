"""Functions and classes to generate Dockerfiles."""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import os
import posixpath

import neurodocker
from neurodocker import interfaces
from neurodocker.utils import apt_get_install, indent, manage_pkgs, yum_install


ND_DIRECTORY = posixpath.join(posixpath.sep, 'neurodocker')
ENTRYPOINT_FILE = posixpath.join(ND_DIRECTORY, 'startup.sh')
SPEC_FILE = posixpath.join(ND_DIRECTORY, 'neurodocker_specs.json')


def _base_add_copy(list_srcs_dest, cmd):
    srcs = list_srcs_dest[:-1]
    dest = list_srcs_dest[-1]

    for src in srcs:
        if os.path.isabs(src):
            raise ValueError("Path for {} cannot be absolute: {}"
                             "".format(cmd, src))
    srcs = '", "'.join(srcs)
    return '{} ["{}", "{}"]'.format(cmd, srcs, dest)


def _add_add(list_srcs_dest, **kwargs):
    """Return Dockerfile ADD instruction to add file or directory to Docker
    image.

    See https://docs.docker.com/engine/reference/builder/#add.

    Parameters
    ----------
    list_srcs_dest : list of str
        All of the items except the last one are paths on local machine or a
        URL to a file to be copied into the Docker container. Paths on the
        local machine must be within the build context. The last item is the
        destination in the Docker image for these file or directories.
    """
    if len(list_srcs_dest) < 2:
        raise ValueError("At least two paths must be provided.")
    return _base_add_copy(list_srcs_dest, "ADD")


def _add_to_entrypoint(bash_cmd, with_run=True):
    """Return command that adds the string `bash_cmd` to second-to-last line of
    entrypoint file.
    """
    import json
    base_cmd = "sed -i '$i{}' $ND_ENTRYPOINT"

    # Escape quotes and remove quotes on either end of string.
    if isinstance(bash_cmd, (list, tuple)):
        escaped_cmds = [json.dumps(c)[1:-1] for c in bash_cmd]
        cmds = [base_cmd.format(c) for c in escaped_cmds]
        cmd = "\n&& ".join(cmds)
    else:
        escaped_bash_cmd = json.dumps(bash_cmd)[1:-1]
        cmd = base_cmd.format(escaped_bash_cmd)
    if with_run:
        comment = "# Add command(s) to entrypoint"
        cmd = indent("RUN", cmd)
        cmd = "\n".join((comment, cmd))
    return cmd


def _add_arg(arg_dict, **kwargs):
    """Return Dockerfile ARG instruction.

    Parameters
    ----------
    arg_dict : dict
        ARG variables where keys are the variable names, and values are the
        values assigned to those variables.
    """
    import json
    cmds = []
    base = "ARG {}"
    for arg, value in arg_dict.items():
        out = base.format(arg)
        if value:  # default value provided.
            value = json.dumps(value)  # Escape double quotes and other things.
            out += "={}".format(value)
        cmds.append(out)
    return "\n".join(cmds)


def _add_base(base, **kwargs):
    """Return Dockerfile FROM instruction to specify base image.

    Parameters
    ----------
    base : str
        Base image.
    """
    return "FROM {}".format(base)


def _add_cmd(cmd, **kwargs):
    """Return Dockerfile CMD instruction."""
    import json

    escaped = json.dumps(cmd)
    return "CMD {}".format(escaped)


def _add_copy(list_srcs_dest, **kwargs):
    """Return Dockerfile COPY instruction to add files or directories to Docker
    image.

    See https://docs.docker.com/engine/reference/builder/#add.

    Parameters
    ----------
    list_srcs_dest : list of str
        All of the items except the last one are paths on local machine to be
        copied into the Docker container. These paths must be within the build
        context. The last item is the destination in the Docker image for these
        file or directories.
    """
    if len(list_srcs_dest) < 2:
        raise ValueError("At least two paths must be provided.")
    return _base_add_copy(list_srcs_dest, "COPY")


def _add_entrypoint(entrypoint, **kwargs):
    """Return Dockerfile ENTRYPOINT instruction to set image entrypoint.

    Parameters
    ----------
    entrypoint : str
        The entrypoint.
    """
    import json

    escaped = json.dumps(entrypoint)
    return "ENTRYPOINT [{}]".format('", "'.join(escaped.split()))


def _add_env_vars(env_vars, **kwargs):
    """Return Dockerfile ENV instruction to set environment variables.

    Parameters
    ----------
    env_vars : dict
        Environment variables where keys are the environment variables names,
        and values are the values assigned to those environment variable names.
    """
    import json
    out = ""
    for k, v in env_vars.items():
        newline = "\n" if out else ""
        v = json.dumps(v)  # Escape double quotes and other things.
        out += '{}{}={}'.format(newline, k, v)
    return indent("ENV", out)


def _add_exposed_ports(exposed_ports, **kwargs):
    """Return Dockerfile EXPOSE instruction to expose ports.

    Parameters
    ----------
    exposed_ports : str, list, tuple
        Port(s) in the container to expose.
    """
    if not isinstance(exposed_ports, (list, tuple)):
        exposed_ports = [exposed_ports]
    return "EXPOSE " + " ".join((str(p) for p in exposed_ports))


def _add_install(pkgs, pkg_manager):
    """Return Dockerfile RUN instruction that installs system packages.

    Parameters
    ----------
    pkgs : list
        List of system packages to install.
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    """
    comment = ("#------------------------"
               "\n# Install system packages"
               "\n#------------------------")
    installers = {'apt': apt_get_install,
                  'yum': yum_install,}
    # pkgs = ' '.join(pkgs)
    # cmd = "{install}\n&& {clean}".format(**manage_pkgs[pkg_manager])
    # cmd = cmd.format(pkgs=pkgs)
    flags = [jj for jj in pkgs if jj.startswith('flags=')]
    pkgs = [kk for kk in pkgs if kk not in flags]

    if flags:
        flags = flags[0].replace('flags=', '')
    else:
        flags = None
    cmd = installers[pkg_manager](pkgs, flags)
    cmd += "\n&& {clean}".format(**manage_pkgs[pkg_manager])
    return indent("RUN", cmd)


def _add_arbitrary_instruction(instruction, **kwargs):
    """Return `instruction` with a comment."""
    comment = "# User-defined instruction\n"
    return comment + instruction


def _add_label(labels, **kwargs):
    """Return Dockerfile LABEL instruction to set image labels.

    Parameters
    ----------
    labels : dict
        Dictionary of label names and values.
    """
    import json
    out = ""
    for k, v in labels.items():
        newline = "\n" if out else ""
        v = json.dumps(v)  # Escape double quotes and other things.
        out += '{}{}={}'.format(newline, k, v)
    return indent("LABEL", out)


def _add_run(cmd, **kwargs):
    """Return Dockerfile RUN instruction."""
    comment = "# User-defined instruction\n"
    return comment + indent("RUN", cmd)


def _add_run_bash(bash_code, **kwargs):
    """Return Dockerfile RUN instruction to execute bash code."""
    comment = "# User-defined BASH instruction\n"
    cmd = 'bash -c "{}"'.format(bash_code.replace('"', '\\"'))
    return comment + indent("RUN", cmd)


def _add_volume(paths, **kwargs):
    """Return Dockerfile VOLUME instruction.

    Parameters
    ----------
    paths : list
        List of paths in the container.
    """
    import json

    escaped = json.dumps(" ".join(paths))
    return "VOLUME [{}]".format('", "'.join(escaped.split()))


def _add_workdir(path, **kwargs):
    """Return Dockerfile WORKDIR instruction to set working directory."""
    return "WORKDIR {}".format(path)


class _DockerfileUsers(object):
    """Class to add instructions to add Dockerfile users. Has memory of users
    already added to the Dockerfile.
    """
    initialized_users = ['root']

    @classmethod
    def add(cls, user, **kwargs):
        instruction = "USER {0}"
        if user not in cls.initialized_users:
            cls.initialized_users.append(user)
            comment = "# Create new user: {0}"
            inst_user = ("RUN useradd --no-user-group --create-home"
                         " --shell /bin/bash {0}")
            instruction = "\n".join((comment, inst_user, instruction))
        return instruction.format(user)

    @classmethod
    def clear_memory(cls):
        cls.initialized_users = ['root']


def _add_spec_json_file(specs):
    """Return Dockerfile instruction to write out specs dictionary to JSON
    file.
    """
    import json

    comment = ("#--------------------------------------"
               "\n# Save container specifications to JSON"
               "\n#--------------------------------------")

    json_specs = json.dumps(specs, indent=2)
    json_specs = json_specs.replace('\\n', '__TO_REPLACE_NEWLINE__')
    json_specs = "\n\\n".join(json_specs.split("\n"))
    # Escape newline characters that the user provided.
    json_specs = json_specs.replace('__TO_REPLACE_NEWLINE__', '\\\\n')
    # Workaround to escape single quotes in a single-quoted string.
    # https://stackoverflow.com/a/1250279/5666087
    json_specs = json_specs.replace("'", """'"'"'""")
    cmd = "echo '{string}' > {path}".format(string=json_specs, path=SPEC_FILE)
    cmd = indent("RUN", cmd)
    return "\n".join((comment, cmd))


def _add_neurodocker_header(specs):
    """Return Dockerfile comment that references Neurodocker."""
    return ("# Generated by Neurodocker v{}."
            "\n#"
            "\n# Thank you for using Neurodocker. If you discover any issues"
            "\n# or ways to improve this software, please submit an issue or"
            "\n# pull request on our GitHub repository:"
            "\n#     https://github.com/kaczmarj/neurodocker"
            "\n#"
            "\n# Timestamp: {}".format(specs['neurodocker_version'],
                                       specs['generation_timestamp']))


def _add_common_dependencies(pkg_manager):
    """Return Dockerfile instructions to download dependencies common to
    many software packages.

    Parameters
    ----------
    pkg_manager : {'apt', 'yum'}
        Linux package manager.
    """
    deps = ['bzip2', 'ca-certificates', 'curl', 'unzip']
    if pkg_manager == "apt":
        deps += ['apt-utils', 'locales']
    if pkg_manager == "yum":
        deps.append('epel-release')
    deps = " ".join(sorted(deps))
    deps = "\n\t" + deps

    comment = ("#----------------------------------------------------------"
               "\n# Install common dependencies and create default entrypoint"
               "\n#----------------------------------------------------------")

    env = ('LANG="en_US.UTF-8"'
           '\nLC_ALL="C.UTF-8"'
           '\nND_ENTRYPOINT="{}"'.format(ENTRYPOINT_FILE))
    env = indent("ENV", env)

    cmd = "{install}\n&& {clean}".format(**manage_pkgs[pkg_manager])
    cmd = cmd.format(pkgs=deps)

    cmd += ("\n&& localedef --force --inputfile=en_US --charmap=UTF-8 C.UTF-8"
            "\n&& chmod 777 /opt && chmod a+s /opt"
            "\n&& mkdir -p /neurodocker"
            '\n&& if [ ! -f "$ND_ENTRYPOINT" ]; then'
            "\n     echo '#!/usr/bin/env bash' >> $ND_ENTRYPOINT"
            "\n     && echo 'set +x' >> $ND_ENTRYPOINT"
            "\n     && echo 'if [ -z \"$*\" ]; then /usr/bin/env bash; else $*; fi' >> $ND_ENTRYPOINT;"
            "\n   fi"
            "\n&& chmod -R 777 /neurodocker && chmod a+s /neurodocker")
    cmd = indent("RUN", cmd)
    entrypoint = 'ENTRYPOINT ["{}"]'.format(ENTRYPOINT_FILE)

    return "\n".join((comment, env, cmd, entrypoint))


# Dictionary of each instruction or software package can be added to the
# Dockerfile and the function that returns the Dockerfile instruction(s).
dockerfile_implementations = {
    # 'software': {
    #     'afni': interfaces.AFNI,
    #     'ants': interfaces.ANTs,
    #     'convert3d': interfaces.Convert3D,
    #     'dcm2niix': interfaces.Dcm2niix,
    #     'freesurfer': interfaces.FreeSurfer,
    #     'fsl': interfaces.FSL,
    #     'miniconda': interfaces.Miniconda,
    #     'mrtrix3': interfaces.MRtrix3,
    #     'neurodebian': interfaces.NeuroDebian,
    #     'spm': interfaces.SPM,
    #     'minc': interfaces.MINC,
    #     'petpvc': interfaces.PETPVC
    # },
    'other': {
        'add': _add_add,
        'add_to_entrypoint':_add_to_entrypoint,
        'arg': _add_arg,
        'base': _add_base,
        'cmd': _add_cmd,
        'copy': _add_copy,
        'entrypoint': _add_entrypoint,
        'expose': _add_exposed_ports,
        'env': _add_env_vars,
        'install': _add_install,
        'instruction': _add_arbitrary_instruction,
        'label': _add_label,
        'run': _add_run,
        'run_bash': _add_run_bash,
        'user': _DockerfileUsers.add,
        'volume': _add_volume,
        'workdir': _add_workdir,
    },
}


def _get_dockerfile_chunk(instruction, options, specs):
    """Return piece of Dockerfile (str) to implement `instruction` with
    `options`. Include the dictionary of specifications.
    """
    software_keys = dockerfile_implementations['software'].keys()
    other_keys = dockerfile_implementations['other'].keys()

    if instruction in software_keys:
        for ii in ['pkg_manager', 'check_urls']:
            options.setdefault(ii, specs[ii])
        callable_ = dockerfile_implementations['software'][instruction]
        chunk = callable_(**options).cmd
    elif instruction in other_keys:
        func = dockerfile_implementations['other'][instruction]
        if instruction == "install":
            chunk = func(options, specs['pkg_manager'])
        else:
            chunk = func(options)
    else:
        raise ValueError("Instruction not understood: {}"
                         "".format(instruction))
    return chunk


def _get_dockerfile_chunks(specs):
    """Return list of Dockerfile chunks (str) given a dictionary of
    specifications.
    """
    import copy
    dockerfile_chunks = []
    specs = copy.deepcopy(specs)

    for instruction, options in specs['instructions']:
        chunk = _get_dockerfile_chunk(instruction, options, specs)
        dockerfile_chunks.append(chunk)

    return dockerfile_chunks


class Dockerfile(object):
    """Class to create Dockerfile.

    Parameters
    ----------
    specs : dict
        Dictionary of specifications.
    """

    def __init__(self, specs):
        from neurodocker.parser import _SpecsParser

        self.specs = specs
        self._add_metadata()
        _SpecsParser(specs)  # Raise exception on error in specs dict.
        self.cmd = self._create_cmd()

        _DockerfileUsers.clear_memory()
        interfaces.Miniconda.clear_memory()

    def __repr__(self):
        return "{self.__class__.__name__}({self.cmd})".format(self=self)

    def __str__(self):
        return self.cmd

    def _add_metadata(self):
        import datetime

        timestamp = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Overwrite already existing metadata.
        self.specs['generation_timestamp'] = timestamp
        self.specs['neurodocker_version'] = neurodocker.__version__

    def _create_cmd(self):
        """Return string representation of Dockerfile."""
        chunks = _get_dockerfile_chunks(self.specs)

        neurodocker_header = _add_neurodocker_header(self.specs)
        common_deps_chunk = _add_common_dependencies(self.specs['pkg_manager'])

        chunks.insert(1, common_deps_chunk)
        chunks.insert(0, neurodocker_header)

        if self.specs['pkg_manager'] == 'apt':
            noninteractive = "ARG DEBIAN_FRONTEND=noninteractive"
            chunks.insert(2, noninteractive)

        chunks.append(_add_spec_json_file(self.specs))

        return "\n\n".join(chunks)

    def save(self, filepath="Dockerfile", **kwargs):
        """Save Dockerfile to `filepath`. `kwargs` are for `open()`."""
        with open(filepath, mode='w', **kwargs) as fp:
            fp.write(self.cmd)
