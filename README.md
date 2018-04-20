# Neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates custom Dockerfiles for neuroimaging and minifies existing Docker images (using [ReproZip](https://www.reprozip.org/)). The package can be used from the command-line or within a Python script. The command-line interface generates Dockerfiles and minifies Docker images, but interaction with the Docker Engine is left to the various `docker` commands. Within a Python script, however, _Neurodocker_ can generate Dockerfiles, build Docker images, run commands within resulting containers (using the [`docker` Python package](https://github.com/docker/docker-py)), and minify Docker images. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces.

Examples:
  - [Generate Dockerfile](#generate-dockerfile)
  - [Generate Dockerfile (full)](#generate-dockerfile-full)
  - [Minimize existing Docker image](#minimize-existing-docker-image)
  - [Example of minimizing Docker image for FreeSurfer recon-all](https://github.com/freesurfer/freesurfer/issues/70#issuecomment-316361886)


# Note to users

This software is still in the early stages of development. If you come across an issue or a way to improve _Neurodocker_, please submit an issue or a pull request.


# Installation

Use the _Neurodocker_ Docker image:

```
docker run --rm kaczmarj/neurodocker:v0.3.1 --help
```

Note: it is not yet possible to minimize Docker containers using the _Neurodocker_ Docker image.


# Supported Software

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
|               | env_name* | Name of this conda environment. |
|               | conda_install | Packages to install with `conda`. E.g., `conda_install="python=3.6 numpy traits"` |
|               | pip_install | Packages to install with `pip`. |
|               | activate | If true (default), activate this environment in container entrypoint. |
| **MRtrix3** | version* | 3.0 |
|             | method | binaries (default) |
|             | install_path | Installation path. Default `/opt/mrtrix3-{version}`. |
| **NeuroDebian** | os_codename* | Codename of the operating system (e.g., stretch, zesty). |
|                 | server* | Server to download NeuroDebian packages from. Choose the one closest to you. See `neurodocker generate docker --help` for the full list of servers. |
|                 | full | If true (default), use non-free sources. If false, use libre sources. |
| **SPM12** | version* | r7219, r6914, r6685, r6472, r6225 |
|           | install_path | Installation path. Default `/opt/spm12-{version}`. |
|           |              | _Note: Matlab Compiler Runtime is installed when SPM12 is installed._ |


\* required argument.  
** FSL is non-free. If you are considering commercial use of FSL, please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).


# Examples

Please see the [examples](examples) directory.

## Canonical example

Generate a Dockerfile which will install ANTs on Ubuntu 17.04. The result can be piped to `docker build` to build the Docker image.

```shell
docker run --rm kaczmarj/neurodocker:v0.3.2 generate -b ubuntu:17.04 -p apt --ants version=2.2.0

docker run --rm kaczmarj/neurodocker:v0.3.2 generate -b ubuntu:17.04 -p apt --ants version=2.2.0 | docker build -
```


## Minimize existing Docker image

The _Neurodocker_ Python package will have to be installed for container minimization:

```shell
pip install --no-cache-dir https://github.com/kaczmarj/neurodocker/tarball/master
```


In the following example, a Docker image is built with ANTs version 2.2.0 and a functional scan. The image is minified for running `antsMotionCorr`. The original ANTs Docker image is 1.85 GB, and the "minified" image is 365 MB.


```shell
# Create a Docker image with ANTs, and download a functional scan.
download_cmd="RUN curl -sSL -o /home/func.nii.gz http://psydata.ovgu.de/studyforrest/phase2/sub-01/ses-movie/func/sub-01_ses-movie_task-movie_run-1_bold.nii.gz"
neurodocker generate -b centos:7 -p yum --ants version=2.2.0 --instruction="$download_cmd" | docker build -t ants:2.2.0 -

# Run the container.
docker run --rm -it --name ants-reprozip-container --security-opt=seccomp:unconfined ants:2.2.0

# (in a new terminal window)
# Output a ReproZip pack file in ~/neurodocker-reprozip-output with the files
# necessary to run antsMotionCorr.
# See https://github.com/stnava/ANTs/blob/master/Scripts/antsMotionCorrExample
cmd="antsMotionCorr -d 3 -a /home/func.nii.gz -o /home/func_avg.nii.gz"
neurodocker reprozip-trace ants-reprozip-container "$cmd"

reprounzip docker setup neurodocker-reprozip.rpz test
```
