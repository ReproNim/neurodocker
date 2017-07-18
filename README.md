# Neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates custom Dockerfiles for neuroimaging and minifies existing Docker images (using [ReproZip](https://www.reprozip.org/)). The package can be used from the command-line or within a Python script. The command-line interface generates Dockerfiles and minifies Docker images, but interaction with the Docker Engine is left to the various `docker` commands. Within a Python script, however, _Neurodocker_ can generate Dockerfiles, build Docker images, run commands within resulting containers (using the [`docker` Python package](https://github.com/docker/docker-py)), and minify Docker images. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces.

Examples:
  - Command-line
    - [Generate Dockerfile (with project's Docker image)](#generate-dockerfile-with-projects-docker-image)
    - [Generate Dockerfile (without project's Docker image)](#generate-dockerfile-without-projects-docker-image)
  - In a Python script
    - [Generate Dockerfile, buid Docker image, run commands in image (minimal)](#generate-dockerfile-buid-docker-image-run-commands-in-image-minimal)
    - [Generate Dockerfile, buid Docker image, run commands in image (full)](#generate-dockerfile-buid-docker-image-run-commands-in-image-full)
      - [Generated Dockerfile](examples/generated-full.Dockerfile)
  - "Minify" Docker image
    - [Minify existing Docker image](#minify-existing-docker-image)


# Note to users

This software is still in the early stages of development. If you come across an issue or a way to improve _Neurodocker_, please submit an issue or a pull request.


# Installation

You can install _Neurodocker_ with `pip`, or you can use the project's Docker image.

`pip install https://github.com/kaczmarj/neurodocker/archive/master.tar.gz`

or

`docker run --rm kaczmarj/neurodocker --help`

Note that building and minifying Docker images is not possible with the _Neurodocker_ Docker image.


# Supported Software

Valid options for each software package are the keyword arguments for the class that installs that package. These classes live in [`neurodocker.interfaces`](neurodocker/interfaces/). The default installation behavior for every software package (except Miniconda) is to install by downloading and un-compressing the binaries.

## ANTs

ANTs can be installed using pre-compiled binaries (default behavior), or it can be compiled from source (takes about 45 minutes). To install ANTs, include `'ants'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'2.2.0'`), `'use_binaries'` (if true, use binaries; if false, compiles from source), and `'git_hash'` (checks out to specific hash before compiling). If `'version'` is latest and `'use_binaries'` is false, builds master branch from source. To install ANTs from NeuroDebian, see the [NeuroDebian interface](#neurodebian).

Repository with pre-compiled binaries: [kaczmarj/ANTs-builds](https://github.com/kaczmarj/ANTs-builds)

View source: [`neurodocker.interfaces.ANTs`](neurodocker/interfaces/ants.py).


## FreeSurfer

FreeSurfer can only be installed using pre-compiled binaries (compiling from source might come in a future update). To install FreeSurfer, include `'freesurfer'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'6.0.0'`) and `'license_path'` (relative path to license.txt). A license is required to run FreeSurfer, but Neurodocker does not provide this license. Add a valid `license.txt` file to the `$FREESURFER_HOME` directory (always /opt/freesurfer) before running FreeSurfer. If `'license_path'` is specified, that file will be copied into the image (note: the relative path to the license file must be within the build context).

View source: [`neurodocker.interfaces.FreeSurfer`](neurodocker/interfaces/freesurfer.py).

## FSL

FSL can be installed using pre-compiled binaries (default behavior), FSL's Python installer (not on Debian-based systems), or through NeuroDebian. To install FSL, include `'fsl'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'5.0.10'`), `'use_binaries'` (bool), and `'use_installer'` (bool; to use FSL's Python installer). To install FSL from NeuroDebian, see the [NeuroDebian interface](#neurodebian).

[FSL license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence)  
View source: [`neurodocker.interfaces.FSL`](neurodocker/interfaces/fsl.py).


## Miniconda

Miniconda is installed using Miniconda's BASH installer. The latest version of Python 3 is installed to the root environment, and the `conda-forge` channel is added. A new conda environment is created with the requested specifications, the root environment is removed (to save space), and the new environment is prepended to `PATH`. To install Miniconda, include `'miniconda'` (case-insensitive) in the specifications dictionary Valid options are `'python_version'` (required; e.g., `'3.5.1'`), `'conda_install'` (e.g., `['numpy', 'traits']`), `pip_install` (e.g., `['nipype', 'pytest']`), and `miniconda_version` (`'latest'` by default).

View source: [`neurodocker.interfaces.Miniconda`](neurodocker/interfaces/miniconda.py).


## MRtrix3

MRtrix3 can be installed using pre-compiled binaries (default behavior), or the package can be built from source. To install MRtrix3, include `'mrtrix3'` (case-insensitive) in the specifications dictionary. Valid options are `'use_binaries'` (bool) and `'git_hash'` (str). If `'git_hash'` is specified, will checkout to that commit before building.


## NeuroDebian

The NeuroDebian repository can be added, and NeuroDebian packages can optionally be installed. Valid keys are os_codename (required; e.g., 'zesty'), download_server (required), full (if false, default, use libre packages), and pkgs (list of NeuroDebian packages to install).

The [NeuroDebian Docker image](https://hub.docker.com/_/neurodebian/) can also be specified as the base image.

View source: [`neurodocker.interfaces.NeuroDebian`](neurodocker/interfaces/neurodebian.py).


## SPM

The standalone version of SPM is installed, along with its dependency Matlab Compiler Runtime (MCR). MCR is installed first, using the [instructions on Matlab's website](https://www.mathworks.com/help/compiler/install-the-matlab-runtime.html). SPM is then installed by downloading and unzipping the standalone SPM package. To install SPM, include `'spm'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'12'`), and `'matlab_version'` (case-sensitive; e.g., `'R2017a'`).

Note: Currently, only SPM12 and MATLAB R2017a are supported.

View source: [`neurodocker.interfaces.SPM`](neurodocker/interfaces/spm.py).



# Examples

## Generate Dockerfile (with project's Docker image)

Generate Dockerfile, and print result to stdout. The result can be piped to `docker build` to build the Docker image.

```shell
docker run --rm kaczmarj/neurodocker generate -b ubuntu:17.04 -p apt --ants version=2.1.0

docker run --rm kaczmarj/neurodocker generate -b ubuntu:17.04 -p apt --ants version=2.1.0 | docker build -
```

## Generate Dockerfile (without project's Docker image)

In this example, a Dockerfile is generated with all of the software that _Neurodocker_ supports, and the Dockerfile is saved to disk. The saved Dockerfile can be passed to `docker build`.

```shell
# Generate Dockerfile.
neurodocker generate -b debian:jessie -p yum \
--ants version=2.1.0 \
--freesurfer version=6.0.0 \
--fsl version=5.0.10 \
--miniconda python_version=3.5.1 conda_install="traits pandas" pip_install=nipype \
--mrtrix3 \
--neurodebian os_codename="jessie" download_server="usa-nh" pkgs="dcm2niix" \
--spm version=12 matlab_version=R2017a \
--instruction='ENTRYPOINT ["python"]'
--no-check-urls --no-print-df -o path/to/project/Dockerfile

# Build Docker image using the saved Dockerfile.
docker build -t myimage path/to/project

# Or pipe the Dockerfile to the docker build command. There is no build
# context in this case.
neurodocker generate -b centos:7 -p yum --ants version=2.2.0 | docker build -
```


## Generate Dockerfile, buid Docker image, run commands in image (minimal)

In this example, a dictionary of specifications is used to generate a Dockerfile. A Docker image is built from the string representation of the Dockerfile. A container is started from that container, and commands are run within the running container. When finished, the container is stopped and removed.


```python
from neurodocker import Dockerfile, SpecsParser
from neurodocker.docker import DockerImage, DockerContainer

specs = {
    'base': 'ubuntu:17.04',
    'pkg_manager': 'apt',
    'check_urls': False,
    'ants': {'version': '2.2.0'}}
}
# Create Dockerfile.
parser = SpecsParser(specs)
df = Dockerfile(parser.specs)

# Build image.
image = DockerImage(df).build(log_console=False, log_filepath="build.log")

# Start container, and run commands.
container = DockerContainer(image).start()
container.exec_run('antsRegistration --help')
container.exec_run('ls /')
container.cleanup(remove=True)
```


## Generate Dockerfile, buid Docker image, run commands in image (full)

In this example, we create a Dockerfile with all of the software that _Neurodocker_ supports, and we supply arbitrary Dockerfile instructions.

```python
from neurodocker import Dockerfile, SpecsParser
from neurodocker.docker import DockerImage, DockerContainer

specs = {
    'base': 'ubuntu:17.04',
    'pkg_manager': 'apt',
    'check_urls': False,
    'miniconda': {
        'python_version': '3.5.1',
        'conda_install': 'traits',
        'pip_install': 'https://github.com/nipy/nipype/archive/master.tar.gz'},
    'ants': {'version': '2.2.0', 'use_binaries': True},
    'freesurfer': {'version': '6.0.0', 'license_path': 'rel/path/license.txt'},
    'fsl': {'version': '5.0.10', 'use_binaries': True},
    'mrtrix3': {'use_binaries': False},
    'neurodebian': {'os_codename': 'zesty', 'download_server': 'usa-nh',
                    'pkgs': ['afni', 'dcm2niix']},
    'spm': {'version': '12', 'matlab_version': 'R2017a'},
    'instruction': ['RUN echo "Hello, World"',
                    'ENTRYPOINT ["run.sh"]']
}

parser = SpecsParser(specs)
df = Dockerfile(parser.specs)
df.save('examples/generated-full.Dockerfile')
print(df)
```

Here is the [Dockerfile](examples/generated-full.Dockerfile) generated by the code above.


## Minify existing Docker image

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
neurodocker reprozip ants-reprozip-container "$cmd"

reprozip docker setup neurodocker-reprozip.rpz test
```
