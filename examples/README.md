# Neurodocker examples

All of the examples below use `debian:stretch` as the base image, but any Docker image can be used as a base. Common base images (and their packages managers) are `ubuntu:16.04` (`apt`), `centos:7` (`yum`), `neurodebian:nd16.04` (`apt`), and `neurodebian:stretch` (`apt`).


Table of contents
-----------------

- [Docker and Singularity options](#docker-and-singularity-options)
  * [`--add-to-entrypoint`](#--add-to-entrypoint)
  * [`--copy`](#--copy)
  * [`--install`](#--install)
  * [`--entrypoint`](#--entrypoint)
  * [`-e / --env`](#-e----env)
  * [`-r / --run`](#-r----run)
  * [`--run-bash`](#--run-bash)
  * [`-u / --user`](#-u----user)
  * [`-w / --workdir`](#-w----workdir)
- [Docker-only options](#docker-only-options)
  * [`--arg`](#--arg)
  * [`--cmd`](#--cmd)
  * [`--expose`](#--expose)
  * [`--label`](#--label)
  * [`--volume`](#--volume)
- [Neuroimaging software examples](#neuroimaging-software-examples)
  * [AFNI](#afni)
  * [ANTs](#ants)
  * [Convert3D](#convert3d)
  * [dcm2niix](#dcm2niix)
  * [FreeSurfer](#freesurfer)
  * [FSL](#fsl)
  * [Matlab Compiler Runtime (MCR)](#matlab-compiler-runtime-mcr)
  * [MINC](#minc)
  * [Miniconda](#miniconda)
  * [MRtrix3](#mrtrix3)
  * [NeuroDebian](#neurodebian)
  * [PETPVC](#petpvc)
  * [SPM12](#spm12)


# Docker and Singularity options

## `--add-to-entrypoint`

This option adds a command to the default container entrypoint, `/neurodocker/startup.sh` and applies to Docker and Singularity. If a container is made with the command below, the command `source /etc/fsl/fsl.sh` will be executed whenever the container is run.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --add-to-entrypoint "source /etc/fsl/fsl.sh"

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --add-to-entrypoint "source /etc/fsl/fsl.sh"
```

If a Docker container is created with the command above and is run with `docker run --rm -it myimage bash`, the command `source /etc/fsl/fsl.sh` will be executed before the `bash` terminal is started.

## `--copy`

This option copies files into the container at build-time and applies to Docker and Singularity.

Docker images that involve copying files must be built with some context, for example `docker build -t myimage .` as opposed to `docker build -t myimage - < Dockerfile`.

```shell
# Docker -- copy the local environment.yml file into the container to /opt/environment.yml.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml

# SIngularity -- copy the local environment.yml file into the container to /opt/environment.yml.
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml
```

## `--install`

This option uses the system package manager to install packages and applies to Docker and Singularity.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --install git vim

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --install git vim
```

## `--entrypoint`

This option sets the container's default entrypoint and applies to Docker and Singularity. It adds an `ENTRYPOINT` layer for Docker and replaces the `%runscript` section for Singularity.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --install curl \
  --entrypoint curl

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --install curl \
  --entrypoint curl
```

In many cases, it is not desirable to overwrite the default entrypoint (`/neurodocker/startup.sh`) because that file sets certain environment variables and activates conda environments. In these cases, they entrypoint can be set as `/neurodocker/startup.sh <your_entrypoint>`. The default entrypoint will be run prior to `<your_entrypoint>`.

In the command below the conda environment `neuro` will be activated prior to running `python`.

```shell
# Docker -- the `neuro` environment is activated before running `python`.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy' \
              activate=true \
  --entrypoint "/neurodocker/startup.sh python"

# Docker -- the `neuro` environment is not activated before running `python`,
# so the default python is used (and numpy will not be available).
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy' \
              activate=true \
  --entrypoint "python"
```

## `-e / --env`

This option sets environment variables in the container and applies to Docker and Singularity. When running a container made with the commands below, the environment variables `$FOO` and `$BAZ` will be available.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --env FOO=bar BAZ=boo

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --env FOO=bar BAZ=boo
```

## `-r / --run`

This option runs arbitrary commands and applies to Docker and Singularity. It creates a new `RUN` layer in Docker and appends to the `%post` section in Singularity.

```shell
# Docker -- download the neurodocker source code
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --run 'curl -LO https://github.com/kaczmarj/neurodocker/tarball/master'

# Singularity -- download the neurodocker source code
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --run 'curl -LO https://github.com/kaczmarj/neurodocker/tarball/master'
```

## `--run-bash`

This option runs an arbitrary command in a bash shell and applies to Docker and Singularity.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --run-bash 'source activate foobar'

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --run-bash 'source activate foobar'
```

## `-u / --user`

This option changes the current user (and adds a new user if necessary) and applies to Docker and Singularity.

```shell
# Docker -- change to non-root user neuro
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --user=neuro

# Singularity -- change to non-root user neurod
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --user=neuro
```

## `-w / --workdir`

This option changes the current working directory and applies to Docker and Singularity.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --workdir=/opt

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --workdir=/opt
```

# Docker-only options

## `--arg`

This option adds a Docker `ARG` layer and does not apply to Singularity. These can be used at container build-time.

```shell
# $FOO is equal to 'bar' by default and $BAZ is unset by default.
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
# Docker -- install pre-compiled binaries.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --afni version=latest method=binaries

# Docker -- build from source.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --afni version=latest method=source

# Singularity -- build from source.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --afni version=latest method=source
```

## ANTs

```shell
# Docker -- build current master branch from source.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --ants version=latest method=source

# Docker -- install binaries for version 2.2.0.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --ants version=2.2.0 method=binaries

# Singularity -- install binaries for version 2.2.0.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --ants version=2.2.0 method=binaries
```

## Convert3D

```shell
# Docker -- install pre-compiled binaries.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --convert3d version=1.0.0 method=binaries

# Singularity -- install pre-compiled binaries.
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --convert3d version=1.0.0 method=binaries
```

## dcm2niix

```shell
# Docker -- compile current master branch
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --dcm2niix version=latest method=source

# Docker -- compile from a specific git commit
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --dcm2niix version=4eb7d5403c56a70ad2a554f954834a335f6bf9a7 method=source

# Singularity -- compile from a specific git commit
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --dcm2niix version=4eb7d5403c56a70ad2a554f954834a335f6bf9a7 method=source
```

## FreeSurfer

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0 method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0 method=binaries

# Docker -- install version minimized for recon-all
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0-min method=binaries

# Docker -- install version minimized for recon-all
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --freesurfer version=6.0.0-min method=binaries
```

## FSL

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --fsl version=5.0.10 method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --fsl version=5.0.10 method=binaries
```

## Matlab Compiler Runtime (MCR)

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --matlabmcr version=2018a method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --matlabmcr version=2018a method=binaries
```

## MINC

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --minc version=1.9.15 method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --minc version=1.9.15 method=binaries
```

## Miniconda

```shell
# Docker -- create a new conda environment and update it in a different layer.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy pandas traits' \
              pip_install='nipype' \
  --miniconda use_env=neuro \
              conda_install='jupyter'

# Docker -- update a conda environment present in the base image.
neurodocker generate docker --base=mybaseimage --pkg-manager=apt \
  --miniconda use_env=neuro \
              conda_install='numpy pandas'

# Docker -- create environment from a YAML file.
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml \
  --miniconda create_env=neuro \
              yaml_file=/opt/environment.yml

# Singularity -- create a new conda environment and update it in a different layer.
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --miniconda create_env=neuro \
              conda_install='python=3.6 numpy pandas traits' \
              pip_install='nipype' \
  --miniconda use_env=neuro \
              conda_install='jupyter'

# Singularity -- update a conda environment present in the base image.
neurodocker generate singularity --base=mybaseimage --pkg-manager=apt \
  --miniconda use_env=neuro \
              conda_install='numpy pandas'

# Singularity -- create environment from a YAML file.
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --copy environment.yml /opt/environment.yml \
  --miniconda create_env=neuro \
              yaml_file=/opt/environment.yml
```

## MRtrix3

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --mrtrix3 version=3.0

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --mrtrix3 version=3.0
```

## NeuroDebian

It is recommended to use the [NeuroDebian Docker images](https://hub.docker.com/_/neurodebian/). If that is not possible, `neurodebian` can be enabled as in the examples below. Software from `neurodebian` can be installed with the `--install` option.

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --neurodebian os_codename=stretch server=usa-nh \
  --install fsl-core

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --neurodebian os_codename=stretch server=usa-nh \
  --install fsl-core
```

## PETPVC

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --petpvc version=1.2.2 method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --petpvc version=1.2.2 method=binaries
```

## SPM12

```shell
# Docker
neurodocker generate docker --base=debian:stretch --pkg-manager=apt \
  --spm12 version=r7219 method=binaries

# Singularity
neurodocker generate singularity --base=debian:stretch --pkg-manager=apt \
  --spm12 version=r7219 method=binaries
```
