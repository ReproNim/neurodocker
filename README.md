# Neurodocker

[![build status](https://img.shields.io/circleci/project/github/kaczmarj/neurodocker/master.svg)](https://circleci.com/gh/kaczmarj/neurodocker/tree/master)
[![docker pulls](https://img.shields.io/docker/pulls/kaczmarj/neurodocker.svg)](https://hub.docker.com/r/kaczmarj/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)

_Neurodocker_ is a command-line program that generates custom Dockerfiles and Singularity recipes for neuroimaging and minifies existing containers.

- Examples:
  - [Examples gallery](./examples)
  - [Canonical examples](#canonical-examples)
    - [Docker](#docker)
    - [Singularity](#singularity)
  - [Minimize existing Docker image](#minimize-existing-docker-image)
  - [Example of minimizing Docker image for FreeSurfer recon-all](https://github.com/freesurfer/freesurfer/issues/70#issuecomment-316361886)
- [Known issues](#known-issues)


# Installation

Use the _Neurodocker_ Singularity image
singularity run shub://tjhendrckson/neurodocker


# Supported software

| software | argument | description |
| -------- | -------- | ----------- |
| **AFNI** | version* | latest |
|          | method   | binaries (default), source. Install pre-compiled binaries or build form source. |
|          | install_path | Installation path. Default `/opt/afni-{version}`. |
|          | install_r | If true, install R. |
|          | install_r_pkgs | If true, install R and AFNI's R packages. |
|          | install_python2 | If true, install Python 2. |
|          | install_python3 | If true, install Python 3. |
| **ANTs** | version* | 2.2.0, 2.1.0, 2.0.3, or 2.0.0. If `method=source`, version can be a git commit hash or branch. |
|          | method   | binaries (default), source. |
|          | install_path | Installation path. Default `/opt/ants-{version}`. |
|          | cmake_opts | If `method=source`, options for `cmake`. |
|          | make_opts | If `method=source`, options for `make`. |
| **Convert3D** | version* | 1.0.0 or nightly. |
|               | method | binaries (default) |
|               | install_path | Installation path. Default `/opt/convert3d-{version}`. |
| **dcm2niix** | version* | latest, git commit hash or branch. |
|              | method | source (default) |
|              | install_path | Installation path. Default `/opt/dcm2niix-{version}`. |
|              | cmake_opts | If `method=source`, options for `cmake`. |
|              | make_opts | If `method=source`, options for `make`. |
| **FreeSurfer** | version* | 6.0.0-min |
|                | method | binaries (default) |
|                | install_path | Installation path. Default `/opt/freesurfer-{version}`. |
|                | exclude_paths | Sequence of space-separated path(s) to exclude when inflating the tarball. |
|                | license_path | Relative path to license file. If provided, this file will be copied into the Docker image. Must be within the build context. |
| **FSL**** | version* | 5.0.11, 5.0.10, 5.0.9, 5.0.8 |
|           | method | binaries (default) |
|           | install_path | Installation path. Default `/opt/fsl-{version}`. |
|           | exclude_paths | Sequence of space-separated path(s) to exclude when inflating the tarball. |
| **Matlab Compiler Runtime** | version* | 2018a, 2012-17[a-b], 2010a |
|                             | method | binaries (default) |
|                             | install_path | Installation path. Default `/opt/matlabmcr-{version}`. |
| **MINC** | version* | 1.9.15 |
|          | method | binaries (default) |
|          | install_path | Installation path. Default `/opt/minc-{version}`. |
| **Miniconda** | version | latest (default), all other hosted versions. |
|               | install_path | Installation path. Default `/opt/miniconda-{version}`. |
|               | create_env | Name of conda environment to create. |
|               | use_env | Name of previously installed environment. |
|               | conda_install | Packages to install with `conda`. E.g., `conda_install="python=3.6 numpy traits"` |
|               | pip_install | Packages to install with `pip`. |
|               | activate | If true (default), activate this environment in container entrypoint. |
| **MRtrix3** | version* | 3.0 |
|             | method | binaries (default) |
|             | install_path | Installation path. Default `/opt/mrtrix3-{version}`. |
| **NeuroDebian** | os_codename* | Codename of the operating system (e.g., stretch, zesty). |
|                 | server* | Server to download NeuroDebian packages from. Choose the one closest to you. See `neurodocker generate docker --help` for the full list of servers. |
|                 | full | If true (default), use non-free sources. If false, use libre sources. |
| **PETPVC** | version* | 1.2.2, 1.2.1, 1.2.0-b, 1.2.0-a, 1.1.0, 1.0.0 |
|            | method | binaries (default) |
|            | install_path | Installation path. Default `/opt/petpvc-{version}`. |
| **SPM12** | version* | r7219, r6914, r6685, r6472, r6225 |
|           | install_path | Installation path. Default `/opt/spm12-{version}`. |
|           |              | _Note: Matlab Compiler Runtime is installed when SPM12 is installed._ |
| **VNC** | passwd* | Choose a password for this VNC server. |
|         | start_at_runtime | If true, start the VNC server at container runtime. False by default. |
|         | geometry | The geometry of the VNC session (e.g., `1920x1080`). |


\* required argument.  
** FSL is non-free. If you are considering commercial use of FSL, please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).


# Generate Dockerfile

```
usage: neurodocker generate docker [-h] [-b BASE] [-p {apt,yum}]
                                   [--add-to-entrypoint ADD_TO_ENTRYPOINT]
                                   [--copy COPY [COPY ...]]
                                   [--install INSTALL [INSTALL ...]]
                                   [--entrypoint ENTRYPOINT]
                                   [-e ENV [ENV ...]] [-r RUN]
                                   [--run-bash RUN_BASH] [-u USER]
                                   [-w WORKDIR] [-f FILE] [-o OUTPUT]
                                   [--no-print] [--afni  [...]]
                                   [--ants  [...]] [--convert3d  [...]]
                                   [--dcm2niix  [...]] [--freesurfer  [...]]
                                   [--fsl  [...]] [--matlabmcr  [...]]
                                   [--minc  [...]] [--miniconda  [...]]
                                   [--mrtrix3 [[...]]] [--neurodebian  [...]]
                                   [--petpvc  [...]] [--spm12  [...]]
                                   [--vnc  [...]] [--add ADD [ADD ...]]
                                   [--arg ARG [ARG ...]] [--cmd CMD [CMD ...]]
                                   [--expose EXPOSE [EXPOSE ...]]
                                   [--label LABEL [LABEL ...]]
                                   [--volume VOLUME [VOLUME ...]]

optional arguments:
  -h, --help            show this help message and exit
  -b BASE, --base BASE  Base Docker image. E.g., debian:stretch
  -p {apt,yum}, --pkg-manager {apt,yum}
                        Linux package manager.
  --add-to-entrypoint ADD_TO_ENTRYPOINT
                        Add a command to the file /neurodocker/startup.sh,
                        which is the container's default entrypoint.
  --copy COPY [COPY ...]
                        Copy files into container. Use format <src>... <dest>
  --install INSTALL [INSTALL ...]
                        Install system packages with apt-get or yum, depending
                        on the package manager specified.
  --entrypoint ENTRYPOINT
                        Set the container's entrypoint (Docker) / append to
                        runscript (Singularity)
  -e ENV [ENV ...], --env ENV [ENV ...]
                        Set environment variable(s). Use the format KEY=VALUE
  -r RUN, --run RUN     Run a command when building container
  --run-bash RUN_BASH   Run a command in bash
  -u USER, --user USER  Switch current user (creates user if necessary)
  -w WORKDIR, --workdir WORKDIR
                        Set working directory
  -f FILE, --file FILE  Generate file from JSON. Overrides other `generate`
                        arguments
  -o OUTPUT, --output OUTPUT
                        If specified, save Dockerfile to file with this name.
  --no-print            Do not print the generated file
  --add ADD [ADD ...]   Dockerfile ADD instruction. Use format <src>... <dest>
  --arg ARG [ARG ...]   Dockerfile ARG instruction. Use format
                        KEY[=DEFAULT_VALUE] ...
  --cmd CMD [CMD ...]   Dockerfile CMD instruction.
  --expose EXPOSE [EXPOSE ...]
                        Dockerfile EXPOSE instruction.
  --label LABEL [LABEL ...]
                        Dockerfile LABEL instruction.
  --volume VOLUME [VOLUME ...]
                        Dockerfile VOLUME instruction.
```

# Generate Singularity recipe

```
usage: neurodocker generate singularity [-h] [-b BASE] [-p {yum,apt}]
                                        [--add-to-entrypoint ADD_TO_ENTRYPOINT]
                                        [--copy COPY [COPY ...]]
                                        [--install INSTALL [INSTALL ...]]
                                        [--entrypoint ENTRYPOINT]
                                        [-e ENV [ENV ...]] [-r RUN]
                                        [--run-bash RUN_BASH] [-u USER]
                                        [-w WORKDIR] [-f FILE] [-o OUTPUT]
                                        [--no-print] [--afni  [...]]
                                        [--ants  [...]] [--convert3d  [...]]
                                        [--dcm2niix  [...]]
                                        [--freesurfer  [...]] [--fsl  [...]]
                                        [--matlabmcr  [...]] [--minc  [...]]
                                        [--miniconda  [...]]
                                        [--mrtrix3 [[...]]]
                                        [--neurodebian  [...]]
                                        [--petpvc  [...]] [--spm12  [...]]
                                        [--vnc  [...]]

optional arguments:
  -h, --help            show this help message and exit
  -b BASE, --base BASE  Base Docker image. E.g., debian:stretch
  -p {apt,yum}, --pkg-manager {apt,yum}
                        Linux package manager.
  --add-to-entrypoint ADD_TO_ENTRYPOINT
                        Add a command to the file /neurodocker/startup.sh,
                        which is the container's default entrypoint.
  --copy COPY [COPY ...]
                        Copy files into container. Use format <src>... <dest>
  --install INSTALL [INSTALL ...]
                        Install system packages with apt-get or yum, depending
                        on the package manager specified.
  --entrypoint ENTRYPOINT
                        Set the container's entrypoint (Docker) / append to
                        runscript (Singularity)
  -e ENV [ENV ...], --env ENV [ENV ...]
                        Set environment variable(s). Use the format KEY=VALUE
  -r RUN, --run RUN     Run a command when building container
  --run-bash RUN_BASH   Run a command in bash
  -u USER, --user USER  Switch current user (creates user if necessary)
  -w WORKDIR, --workdir WORKDIR
                        Set working directory
  -f FILE, --file FILE  Generate file from JSON. Overrides other `generate`
                        arguments
  -o OUTPUT, --output OUTPUT
                        If specified, save Dockerfile to file with this name.
  --no-print            Do not print the generated file
```

# Examples

Please see the [examples](examples) directory.

## Canonical examples

The canonical examples install ANTs version 2.2.0 on Debian 9 (Stretch).


### Docker

```shell
$ singularity exec --rm kaczmarj/neurodocker:0.4.1 neurodocker generate docker \
    --base debian:stretch --pkg-manager apt --ants version=2.2.0
```
### Singularity

Install ANTs on Debian 9 (Stretch).

```shell
$ singularity exec --rm kaczmarj/neurodocker:0.4.1 neurodocker generate singularity \
    --base debian:stretch --pkg-manager apt --ants version=2.2.0
```


## Minimize existing Docker image

_Neurodocker_ must be `pip` installed for container minimization.

In the following example, a Docker image is built with ANTs version 2.2.0 and a functional scan. The image is minified for running `antsMotionCorr`. The original ANTs Docker image is 1.85 GB, and the "minified" image is 365 MB.


```shell
# Create a Docker image with ANTs, and download a functional scan.
$ download_cmd="curl -sSL -o /home/func.nii.gz http://psydata.ovgu.de/studyforrest/phase2/sub-01/ses-movie/func/sub-01_ses-movie_task-movie_run-1_bold.nii.gz"
$ neurodocker generate docker -b centos:7 -p yum --ants version=2.2.0 --run="$download_cmd" | docker build -t ants:2.2.0 -

# Run the container in the background.
# The option --security-opt=seccomp:unconfined is important. Without this,
# the trace will not be able to run in the container.
$ docker run --rm -itd --name ants-container --security-opt=seccomp:unconfined ants:2.2.0

# Output a ReproZip pack file in the current directory with the files
# necessary to run antsMotionCorr.
$ cmd="antsMotionCorr -d 3 -a /home/func.nii.gz -o /home/func_avg.nii.gz"
$ neurodocker reprozip trace ants-container "$cmd"
# Create a Docker container with the contents of ReproZip's trace.
$ reprounzip docker setup neurodocker-reprozip.rpz test
```


# Known issues

- Using the `-t/--tty` option in `docker run` produces non-printable characters in the generated Dockerfile or Singularity recipe (see [moby/moby#8513 (comment)](https://github.com/moby/moby/issues/8513#issuecomment-216191236)).
  - Solution: do not use the `-t/--tty` flag, unless using the container interactively.
- Attempting to rebuild into an existing Singularity image may raise an error.
  - Solution: remove the existing image or build a new image file.
- The default apt --install option "--no-install-recommends" (that aims at minimizing container sizes) can cause a strange behaviour for cython inside the container
  - Solution: use "--install apt_opts=`--quiet` "
  - more information: [examples](examples#--install)
