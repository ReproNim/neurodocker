# Neurodocker examples

All of the examples below use `debian:stretch` as the base image, but any Docker image can be used as a base. Common base images (and their packages managers) are `ubuntu:16.04` (`apt`), `centos:7` (`yum`), `neurodebian:nd16.04` (`apt`), and `neurodebian:stretch` (`apt`).

## Table of contents

- [Docker and Singularity options](#docker-and-singularity-options)
  - [`--add-to-entrypoint`](#--add-to-entrypoint)
  - [`--copy`](#--copy)
  - [`--install`](#--install)
  - [`--entrypoint`](#--entrypoint)
  - [`-e / --env`](#-e----env)
  - [`-r / --run`](#-r----run)
  - [`--run-bash`](#--run-bash)
  - [`-u / --user`](#-u----user)
  - [`-w / --workdir`](#-w----workdir)
- [Docker-only options](#docker-only-options)
  - [`--arg`](#--arg)
  - [`--cmd`](#--cmd)
  - [`--expose`](#--expose)
  - [`--label`](#--label)
  - [`--volume`](#--volume)
- [Neuroimaging software examples](#neuroimaging-software-examples)
  - [AFNI](#afni)
  - [ANTs](#ants)
  - [Convert3D](#convert3d)
  - [dcm2niix](#dcm2niix)
  - [FreeSurfer](#freesurfer)
  - [FSL](#fsl)
  - [Matlab Compiler Runtime (MCR)](#matlab-compiler-runtime-mcr)
  - [MINC](#minc)
  - [Miniconda](#miniconda)
  - [MRtrix3](#mrtrix3)
  - [NeuroDebian](#neurodebian)
  - [PETPVC](#petpvc)
  - [SPM12](#spm12)
  - [VNC](#vnc)
- [JSON](#json)
- [NeuroDebian Freeze](#neurodebian-freeze)

# Docker and Singularity options

## `--add-to-entrypoint`

This option adds a command to the default container entrypoint, `/neurodocker/startup.sh` and applies to Docker and Singularity. If a container is made with the command below, the command `source /etc/fsl/fsl.sh` will be executed whenever the container is run.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --add-to-entrypoint "source /etc/fsl/fsl.sh"
```

If a Docker container is created with the command above and is run with `docker run --rm -it myimage bash`, the command `source /etc/fsl/fsl.sh` will be executed before the `bash` terminal is started.

## `--copy`

This option copies files into the container at build-time and applies to Docker and Singularity.

Docker images that involve copying files must be built with some context, for example `docker build -t myimage .` as opposed to `docker build -t myimage - < Dockerfile`.

```shell
# Copy the local environment.yml file into the container to /opt/environment.yml.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml
```

## `--install`

This option uses the system package manager to install packages and applies to Docker and Singularity.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --install git vim
```

one can use apt_opts to set options for apt-get install and yum_opts to set options for yum install:

```shell
neurodocker generate [docker|singularity] --base=centos:7 --pkg-manager=yum \
  --install yum_opts='--debug' git vim
```

By default --install apt_opts uses --no-install-recommends to minimize container sizes. In few cases this can lead to unexpected behaviours and one can try to build a container without this option.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --install apt_opts='--quiet' git vim
```

## `--entrypoint`

This option sets the container's default entrypoint and applies to Docker and Singularity. It adds an `ENTRYPOINT` layer for Docker and replaces the `%runscript` section for Singularity.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --entrypoint curl
```

In many cases, it is not desirable to overwrite the default entrypoint (`/neurodocker/startup.sh`) because that file sets certain environment variables and activates conda environments. In these cases, the entrypoint can be set as `/neurodocker/startup.sh <your_entrypoint>`. The default entrypoint will be run prior to `<your_entrypoint>`.

In the command below the conda environment `neuro` will be activated prior to running `python`.

```shell
# The `neuro` environment is activated before running `python`.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy' \
              activate=true \
  --entrypoint "/neurodocker/startup.sh python"

# The `neuro` environment is not activated before running `python`,
# so the default python is used (and numpy will not be available).
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy' \
              activate=true \
  --entrypoint "python"
```

## `-e / --env`

This option sets environment variables in the container and applies to Docker and Singularity. When running a container made with the commands below, the environment variables `$FOO` and `$BAZ` will be available.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --env FOO=bar BAZ=boo
```

## `-r / --run`

This option runs arbitrary commands and applies to Docker and Singularity. It creates a new `RUN` layer in Docker and appends to the `%post` section in Singularity.

```shell
# Download the neurodocker source code
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --run 'curl -LO https://github.com/kaczmarj/neurodocker/tarball/master'
```

## `--run-bash`

This option runs an arbitrary command in a bash shell and applies to Docker and Singularity.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --run-bash 'source activate foobar'
```

## `-u / --user`

This option changes the current user (and adds a new user if necessary) and applies to Docker and Singularity.

```shell
# Change to non-root user neuro
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --user=neuro
```

## `-w / --workdir`

This option changes the current working directory and applies to Docker and Singularity.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --workdir=/opt
```

# Docker-only options

## `--arg`

This option adds a Docker `ARG` layer and does not apply to Singularity. These can be used at container build-time.

```shell
# $FOO is set to 'bar' by default and $BAZ is unset by default.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --arg FOO=bar BAZ
```

## `--cmd`

This option adds a Docker `CMD` layer and does not apply to Singularity. The `CMD` can be thought of as command-line arguments to the `ENTRYPOINT`.

```shell
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --cmd echo "i am in the container"
```

## `--expose`

This option adds a Docker `EXPOSE` layer and does not apply to Singularity.

```shell
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --expose 8888 6006
```

## `--label`

This option adds a Docker `LABEL` layer and does not apply to Singularity.

```shell
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --label maintainer="Jakub Kaczmarzyk <jakubk@mit.edu>"
```

## `--volume`

This option adds a Docker `VOLUME` layer and does not apply to Singularity.

```shell
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --volume /data
```

# Neuroimaging software examples

## AFNI

```shell
# Install pre-compiled binaries.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --afni version=latest method=binaries

# Build from source.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --afni version=latest method=source
```

## ANTs

```shell
# Build current master branch from source.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --ants version=latest method=source

# Install binaries for version 2.2.0.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --ants version=2.2.0 method=binaries
```

## Convert3D

```shell
# Install pre-compiled binaries.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --convert3d version=1.0.0 method=binaries
```

## dcm2niix

```shell
# Compile current master branch
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --dcm2niix version=latest method=source

# Compile from a specific git commit
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --dcm2niix version=4eb7d5403c56a70ad2a554f954834a335f6bf9a7 method=source
```

## FreeSurfer

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0 method=binaries

# Install version minimized for recon-all
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0-min method=binaries
```

## FSL

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --fsl version=5.0.10 method=binaries
```

## Matlab Compiler Runtime (MCR)

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --matlabmcr version=2018a method=binaries
```

## MINC

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --minc version=1.9.15 method=binaries
```

## Miniconda

```shell
# Create a new conda environment and update it in a different layer.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy pandas traits' \
              pip_install='nipype' \
  --miniconda use_env=neuro \
              conda_install='jupyter'

# Update a conda environment present in the base image.
neurodocker generate [docker|singularity] --base=mybaseimage --pkg-manager=apt \
  --miniconda use_env=neuro \
              conda_install='numpy pandas'

# Create environment from a YAML file.
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml \
  --miniconda create_env=neuro \
              yaml_file=/opt/environment.yml
```

## MRtrix3

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --mrtrix3 version=3.0_RC3
```

## NeuroDebian

It is recommended to use the [NeuroDebian Docker images](https://hub.docker.com/_/neurodebian/). If that is not possible, `neurodebian` can be enabled as in the examples below. Software from `neurodebian` can be installed with the `--install` option.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --neurodebian os_codename=stretch server=usa-nh \
  --install fsl-core
```

## PETPVC

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --petpvc version=1.2.2 method=binaries
```

## SPM12

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --spm12 version=r7219 method=binaries
```

## VNC

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --vnc passwd=hunter2 start_at_runtime=true geometry=1920x1080 \
  --install xterm
```

If a Docker image (e.g., `vnc_image`) is built with this command, one can run a GUI application like this:

```shell
docker run --rm -it -p 5901:5901 vnc_image xterm
```

In a VNC client, connect to 127.0.0.1:5901, and enter the password used when configuring the container. `xterm` is a graphical terminal. It is used only as an example. Any GUI program can be used (e.g., Firefox).

# JSON

Neurodocker can generate Dockerfiles and Singularity files from JSON. For example, the file `example_specs.json` (contents below) can be used to with `neurodocker generate` as follows:

```json
{
  "pkg_manager": "apt",
  "instructions": [
    ["base", "debian"],
    [
      "ants",
      {
        "version": "2.2.0"
      }
    ],
    ["install", ["git"]],
    [
      "miniconda",
      {
        "create_env": "neuro",
        "conda_install": ["numpy", "traits"],
        "pip_install": ["nipype"]
      }
    ]
  ]
}
```

```shell
neurodocker generate [docker|singularity] example_spec.json
```

The JSON representation of a particular `neurodocker generate` command can be printed by adding the `--json` flag. The JSON representation above was found using the code snippet below.

```shell
neurodocker generate [docker|singularity] --base=debian:stretch --pkg-manager=apt \
  --ants version=2.2.0 \
  --install git \
  --miniconda create_env=neuro \
              conda_install='numpy traits' \
              pip_install='nipype' \
  --json
```

# NeuroDebian Freeze

Use this with NeuroDebian distributions to pin the `apt` sources to a specific date (and optionally time). This can greatly help to produce a reproducible container specification, because all calls to `apt-get update` will point to the same snapshots of packages. Please see the script [`nd_freeze`](http://neuro.debian.net/pkgs/neurodebian-freeze.html) for more information. The usage is as follows:

```shell
neurodocker generate [docker|singularity] --base=neurodebian:stretch --pkg-manager=apt \
  --ndfreeze date=20180312
```

The call to `nd_freeze` will occur close to the beginning of the Docker or Singularity specification, regardless of the position of `--ndfreeze` on the command line.
