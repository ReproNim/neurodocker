# Neurodocker

[![build status](https://img.shields.io/circleci/project/github/ReproNim/neurodocker/master.svg)](https://circleci.com/gh/ReproNim/neurodocker/tree/master)
[![docker pulls](https://img.shields.io/docker/pulls/repronim/neurodocker.svg)](https://hub.docker.com/r/repronim/neurodocker/)
[![docker pulls](https://img.shields.io/docker/pulls/kaczmarj/neurodocker.svg)](https://hub.docker.com/r/kaczmarj/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)
[![DOI](https://zenodo.org/badge/88654995.svg)](https://zenodo.org/badge/latestdoi/88654995)

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

Use the _Neurodocker_ Docker image (recommended):

```shell
docker run --rm repronim/neurodocker:0.7.0 --help
```

The Docker images were recently moved to [repronim/neurodocker](https://hub.docker.com/r/repronim/neurodocker) from [kaczmarj/neurodocker](https://hub.docker.com/r/kaczmarj/neurodocker).

_Note_: Do not use the `-t/--tty` flag with `docker run` or non-printable characters will be a part of the output (see [moby/moby#8513 (comment)](https://github.com/moby/moby/issues/8513#issuecomment-216191236)).

This project can also be installed with `pip`:

```shell
pip install neurodocker
neurodocker --help
```

If the `pip install` command above gives a permissions error, install as a non-root user:

```shell
pip install --user neurodocker
```

Note: it is not yet possible to minimize Docker containers using the _Neurodocker_ Docker image.

# Supported software

| software                    | argument         | description                                                                                                                                         |
| --------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AFNI**                    | version\*        | latest                                                                                                                                              |
|                             | method           | binaries (default), source. Install pre-compiled binaries or build form source.                                                                     |
|                             | install_path     | Installation path. Default `/opt/afni-{version}`.                                                                                                   |
|                             | install_r        | If true, install R.                                                                                                                                 |
|                             | install_r_pkgs   | If true, install R and AFNI's R packages.                                                                                                           |
|                             | install_python2  | If true, install Python 2.                                                                                                                          |
|                             | install_python3  | If true, install Python 3.                                                                                                                          |
| **ANTs**                    | version\*        | 2.3.4, 2.3.2, 2.3.1, 2.3.0, 2.2.0, 2.1.0, 2.0.3, or 2.0.0. If `method=source`, version can be a git commit hash or branch.                                        |
|                             | method           | binaries (default), source.                                                                                                                         |
|                             | install_path     | Installation path. Default `/opt/ants-{version}`.                                                                                                   |
|                             | cmake_opts       | If `method=source`, options for `cmake`.                                                                                                            |
|                             | make_opts        | If `method=source`, options for `make`.                                                                                                             |
| **Convert3D**               | version\*        | 1.0.0 or nightly.                                                                                                                                   |
|                             | method           | binaries (default)                                                                                                                                  |
|                             | install_path     | Installation path. Default `/opt/convert3d-{version}`.                                                                                              |
| **dcm2niix**                | version\*        | latest, git commit hash or branch.                                                                                                                  |
|                             | method           | source (default)                                                                                                                                    |
|                             | install_path     | Installation path. Default `/opt/dcm2niix-{version}`.                                                                                               |
|                             | cmake_opts       | If `method=source`, options for `cmake`.                                                                                                            |
|                             | make_opts        | If `method=source`, options for `make`.                                                                                                             |
| **FreeSurfer**              | version\*        | 7.1.0, 6.0.1, 6.0.0, 6.0.0-min |
|                             | method           | binaries (default) |
|                             | install_path     | Installation path. Default `/opt/freesurfer-{version}`. |
|                             | exclude_paths    | Sequence of space-separated path(s) to exclude when inflating the tarball.                                                                          |
| **FSL\*\***                 | version\*        | 6.0.3, 6.0.2, 6.0.1, 6.0.0, 5.0.11, 5.0.10, 5.0.9, 5.0.8                                                                                                                        |
|                             | method           | binaries (default)                                                                                                                                  |
|                             | install_path     | Installation path. Default `/opt/fsl-{version}`.                                                                                                    |
|                             | exclude_paths    | Sequence of space-separated path(s) to exclude when inflating the tarball.                                                                          |
| **ITKsnap**                 | version\*        | 3.8.0 |
|                             | method           | binaries (default)|
|                             | install_path     | Installation path. Default `/opt/itksnap-{version}`. |
| **Matlab Compiler Runtime** | version\*        | 2018a, 2012-17[a-b], 2010a                                                                                                                          |
|                             | method           | binaries (default)                                                                                                                                  |
|                             | install_path     | Installation path. Default `/opt/matlabmcr-{version}`.                                                                                              |
| **MINC**                    | version\*        | 1.9.17, 1.9.16, 1.9.15 |
|                             | method           | binaries (default) |
|                             | install_path     | Installation path. Default `/opt/minc-{version}`. |
| **Miniconda**               | version          | latest (default), all other hosted versions.                                                                                                        |
|                             | install_path     | Installation path. Default `/opt/miniconda-{version}`.                                                                                              |
|                             | create_env       | Name of conda environment to create.                                                                                                                |
|                             | use_env          | Name of previously installed environment.                                                                                                           |
|                             | conda_install    | Packages to install with `conda`. E.g., `conda_install="python=3.6 numpy traits"`                                                                   |
|                             | pip_install      | Packages to install with `pip`.                                                                                                                     |
|                             | activate         | If true (default), activate this environment in container entrypoint.                                                                               |
| **MRIcron** | version\* | latest, 1.0.20190902, 1.0.20190410, 1.0.20181114, 1.0.20180614, 1.0.20180404, 1.0.20171220 |
| | install_path | Installation path. Default `/opt/mricron-{version}` |
| **MRtrix3**                 | version\*        | 3.0                                                                                                                                                 |
|                             | method           | binaries (default)                                                                                                                                  |
|                             | install_path     | Installation path. Default `/opt/mrtrix3-{version}`.                                                                                                |
| **NeuroDebian**             | os_codename\*    | Codename of the operating system (e.g., stretch, zesty).                                                                                            |
|                             | server\*         | Server to download NeuroDebian packages from. Choose the one closest to you. See `neurodocker generate docker --help` for the full list of servers. |
|                             | full             | If true (default), use non-free sources. If false, use libre sources.                                                                               |
| **PETPVC**                  | version\*        | 1.2.2, 1.2.1, 1.2.0-b, 1.2.0-a, 1.1.0, 1.0.0                                                                                                        |
|                             | method           | binaries (default)                                                                                                                                  |
|                             | install_path     | Installation path. Default `/opt/petpvc-{version}`.                                                                                                 |
| **SPM12**                   | version\*        | r7219, r6914, r6685, r6472, r6225                                                                                                                   |
|                             | install_path     | Installation path. Default `/opt/spm12-{version}`.                                                                                                  |
|                             |                  | _Note: Matlab Compiler Runtime is installed when SPM12 is installed._                                                                               |
| **VNC**                     | passwd\*         | Choose a password for this VNC server.                                                                                                              |
|                             | start_at_runtime | If true, start the VNC server at container runtime. False by default.                                                                               |
|                             | geometry         | The geometry of the VNC session (e.g., `1920x1080`).                                                                                                |

\* required argument.
\*\* FSL is non-free. If you are considering commercial use of FSL, please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).

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

The canonical examples install ANTs version 2.3.1 on Debian 9 (Stretch).

_Note_: Do not use the `-t/--tty` flag with `docker run` or non-printable characters will be a part of the output (see [moby/moby#8513 (comment)](https://github.com/moby/moby/issues/8513#issuecomment-216191236)).

### Docker

```shell
docker run --rm repronim/neurodocker:0.7.0 generate docker \
    --base debian:stretch --pkg-manager apt --ants version=2.3.1

# Build image by piping Dockerfile to `docker build`
docker run --rm repronim/neurodocker:0.7.0 generate docker \
    --base debian:stretch --pkg-manager apt --ants version=2.3.1 | docker build -
```

### Singularity

Install ANTs on Debian 9 (Stretch).

```shell
docker run --rm repronim/neurodocker:0.7.0 generate singularity \
    --base debian:stretch --pkg-manager apt --ants version=2.3.1
```

## Minimize existing Docker image

_Neurodocker_ must be `pip` installed for container minimization. The `docker` Python package must also be installed.

In the following example, a Docker image is built with ANTs version 2.3.1 and a functional scan. The image is minified for running `antsMotionCorr`. The original ANTs Docker image is 1.97 GB, and the "minified" image is 293 MB. The only directory that is pruned is `/opt`, which includes the ANTs installation. This means that important directories like `/usr` and `/bin` are untouched, and the container can still be used interactively.

```shell
# Create a Docker image with ANTs, and download a functional scan.
download_cmd="curl -sSL -o /home/func.nii.gz http://psydata.ovgu.de/studyforrest/phase2/sub-01/ses-movie/func/sub-01_ses-movie_task-movie_run-1_bold.nii.gz"
neurodocker generate docker -b centos:7 -p yum --ants version=2.3.1 --run="$download_cmd" | docker build -t ants:2.3.1 -

# Run the container in the background. The option --security-opt=seccomp:unconfined is
# important. Without this, the trace will not be able to run in the container.
docker run --rm -itd --name ants-container --security-opt=seccomp:unconfined ants:2.3.1

# Find all of the files under `/opt` that are not used by the command(s), and queue
# those files for deletion.
cmd="antsMotionCorr -d 3 -a /home/func.nii.gz -o /home/func_avg.nii.gz"
neurodocker-minify --container ants-container --dirs-to-prune /opt --commands "$cmd"
# Read through the list of files that will be deleted, and respond with the keyboard.
# Then, create a new Docker image using the pruned container.
docker export ants-container | docker import - ants:2.3.1-min-motioncorr

# View a summary of the Docker images.
docker images
# REPOSITORY          TAG                    IMAGE ID            CREATED              SIZE
# ants                2.3.1-min-motioncorr   6436f58e965c        About a minute ago   293MB
# ants                2.3.1                  b56f5e9d1805        17 minutes ago       1.97GB
# centos              7                      5e35e350aded        4 months ago         203MB
```

# Known issues

- Using the `-t/--tty` option in `docker run` produces non-printable characters in the generated Dockerfile or Singularity recipe (see [moby/moby#8513 (comment)](https://github.com/moby/moby/issues/8513#issuecomment-216191236)).
  - Solution: do not use the `-t/--tty` flag, unless using the container interactively.
- Attempting to rebuild into an existing Singularity image may raise an error.
  - Solution: remove the existing image or build a new image file.
- The default apt `--install` option `--no-install-recommends` (that aims at minimizing container sizes) can cause unexpected behavior.
  - Solution: use `--install apt_opts="--quiet"`
  - Please see the [examples](examples#--install) for more information.
- FreeSurfer cannot find my license file.
  - Solution: get a free license from [FreeSurfer's website](https://surfer.nmr.mgh.harvard.edu/registration.html), and copy it into the container. To build the Docker image, please use the form `docker build .` instead of `docker build - < Dockerfile`. The latter form will not copy files into the image.
  - Please see the [examples](examples#freesurfer) for more information.
