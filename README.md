# Neurodocker

[![build status](https://img.shields.io/circleci/project/github/kaczmarj/neurodocker/master.svg)](https://circleci.com/gh/kaczmarj/neurodocker/tree/master)
[![docker pulls](https://img.shields.io/docker/pulls/kaczmarj/neurodocker.svg)](https://hub.docker.com/r/kaczmarj/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)

_Neurodocker_ is a command-line program that generates custom Dockerfiles and Singularity recipes for neuroimaging and minifies existing containers.

Examples:
  - [Canonical examples](#canonical-examples)
    - [Docker](#docker)
    - [Singularity](#singularity)
  - [Assorted examples](./examples)
  - [Minimize existing Docker image](#minimize-existing-docker-image)
  - [Example of minimizing Docker image for FreeSurfer recon-all](https://github.com/freesurfer/freesurfer/issues/70#issuecomment-316361886)


# Installation

Use the _Neurodocker_ Docker image (recommended):

```shell
$ docker run --rm kaczmarj/neurodocker:0.4.0rc1 --help
```

This project can also be installed with `pip`:

```shell
$ pip install neurodocker
$ neurodocker --help
```

If the `pip install` command above gives a permissions error, install as a non-root user:

```shell
$ pip install --user neurodocker
```

Note: it is not yet possible to minimize Docker containers using the _Neurodocker_ Docker image.


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
|                | exclude_paths | Sequence of path(s) to exclude when inflating the tarball. |
|                | license_path | Relative path to license file. If provided, this file will be copied into the Docker image. Must be within the build context. |
| **FSL**** | version* | 5.0.11, 5.0.10, 5.0.9, 5.0.8 |
|           | method | binaries (default) |
|           | install_path | Installation path. Default `/opt/fsl-{version}`. |
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


\* required argument.  
** FSL is non-free. If you are considering commercial use of FSL, please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).


# Examples

Please see the [examples](examples) directory.

## Canonical examples

The canonical examples install ANTs version 2.2.0 on Ubuntu 18.04.

### Docker

```shell
$ docker run --rm kaczmarj/neurodocker:0.4.0rc1 generate docker \
    --base ubuntu:18.04 --pkg-manager apt --ants version=2.2.0

# Build image by piping Dockerfile to `docker build`
$ docker run --rm kaczmarj/neurodocker:0.4.0rc1 generate docker \
    --base ubuntu:18.04 --pkg-manager apt --ants version=2.2.0 | docker build -
```

### Singularity

Install ANTs on Ubuntu 18.04.

```shell
$ docker run --rm kaczmarj/neurodocker:0.4.0rc1 generate singularity \
    --base ubuntu:18.04 --pkg-manager apt --ants version=2.2.0
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
