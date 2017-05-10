# neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates Dockerfiles with specified versions of Python and neuroimaging analysis software. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces. _Neurodocker_ can be used from the command-line or within a Python script. The command-line interface generates Dockerfiles, and interaction with the Docker Engine is left to the various `docker` commands. Within a script, however, _Neurodocker_ can generate Dockerfiles, build Docker images, and run commands within resulting containers (using the [`docker` Python package](https://github.com/docker/docker-py)).

See the [examples](#examples) below.


# Installation

You can install _Neurodocker_ with `pip`, or you can use the project's Docker image.

`pip install https://github.com/kaczmarj/neurodocker/archive/master.tar.gz`

or

`docker run --rm kaczmarj/neurodocker --help`


Note: the `docker` Python package must be installed to build images and run containers with _Neurodocker_: `pip install docker`.




## Supported Software

Valid options for each software package are the keyword arguments for the class that installs that package. These classes live in [`neurodocker.interfaces`](neurodocker/interfaces/). The default installation behavior for every software package (except Miniconda) is to install by downloading and un-compressing the binaries.

### ANTs

ANTs can be installed using pre-compiled binaries (default behavior), or it can be built from source (takes about 45 minutes). To install ANTs, include `'ants'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'2.1.0'`) and `'use_binaries'` (if true, use binaries; if false, build from source).

View source: [`neurodocker.interfaces.ANTs`](neurodocker/interfaces/ants.py).

### FSL

FSL can be installed using pre-compiled binaries (default behavior), FSL's Python installer (not on Debian-based systems), or through NeuroDebian. To install FSL, include `'fsl'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'5.0.10'`), `'use_binaries'` (bool), `'use_installer'` (bool; to use FSL's Python installer), `'use_neurodebian'` (bool), and `'os_codename'` (e.g., `'jessie'` or `'xenial'`; only required if installing with NeuroDebian).

View source: [`neurodocker.interfaces.FSL`](neurodocker/interfaces/fsl.py).


### Miniconda

Miniconda is installed using Miniconda's BASH installer. The latest version of Python 3 is installed to the root environment, and the `conda-forge` channel is added. A new conda environment is created with the requested specifications, the root environment is removed (to save space), and the new environment is prepended to `PATH`. To install Miniconda, include `'miniconda'` (case-insensitive) in the specifications dictionary Valid options are `'python_version'` (required; e.g., `'3.5.1'`), `'conda_install'` (e.g., `['numpy', 'traits']`), `pip_install` (e.g., `['nipype', 'pytest']`), and `miniconda_version` (`'latest'` by default).

View source: [`neurodocker.interfaces.Miniconda`](neurodocker/interfaces/miniconda.py).


### SPM

The standalone version of SPM is installed, along with its dependency Matlab Compiler Runtime (MCR). MCR is installed first, using the [instructions on Matlab's website](https://www.mathworks.com/help/compiler/install-the-matlab-runtime.html). SPM is then installed by downloading and unzipping the standalone SPM package. To install SPM, include `'spm'` (case-insensitive) in the specifications dictionary. Valid options are `'version'` (e.g., `'12'`), and `'matlab_version'` (case-sensitive; e.g., `'R2017a'`).

Note: Currently, only SPM12 and MATLAB R2017a are supported.

View source: [`neurodocker.interfaces.SPM`](neurodocker/interfaces/spm.py).



# Examples

## Using the project's Docker image

Generate Dockerfile, and print result to stdout.

```bash
docker run --rm kaczmarj/neurodocker -b ubuntu:17.04 -p apt \
--ants version=2.1.0 \
--fsl version=5.0.10 \
--miniconda python_version=3.5.1 conda_install=traits,pandas pip_install=nipype \
--spm version=12 matlab_version=R2017a \
--no-check-urls
```

## Command-line example

Generate Dockerfile, do not print result to stdout, save to file. Build the Docker image with `docker build`.

Example:

```bash
# Generate Dockerfile.
neurodocker -b centos:7 -p yum \
--ants version=2.1.0 \
--fsl version=5.0.10 \
--miniconda python_version=3.5.1 conda_install=traits,pandas pip_install=nipype \
--spm version=12 matlab_version=R2017a \
--no-check-urls --no-print-df -o path/to/project/Dockerfile

# Build Docker image using the saved Dockerfile.
docker build -t myimage path/to/project

# Or pipe the Dockerfile to the docker build command. There is no build
# context in this case.
neurodocker -b centos:7 -p yum --miniconda python_version=3.5.1 | docker build -
```


## Scripting example


In the following example, a dictionary of specifications is used to generate a Dockerfile. A Docker image is built from the string representation of the Dockerfile. A container is started from that container, and commands are run within the running container. When finished, the container is stopped and removed.


```python
from neurodocker import Dockerfile, SpecsParser
from neurodocker.docker import DockerImage, DockerContainer

specs = {
    'base': 'ubuntu:17.04',
    'pkg_manager': 'apt',
    'check_urls': False,  # Verify communication with URLs used in build.
    'miniconda': {
        'python_version': '3.5.1',
        'conda_install': 'traits',
        'pip_install': 'https://github.com/nipy/nipype/archive/master.tar.gz'},
    'ants': {'version': '2.1.0', 'use_binaries': True},
    'fsl': {'version': '5.0.10', 'use_binaries': True},
    'spm': {'version': '12', 'matlab_version': 'R2017a'},
}

parser = SpecsParser(specs)
df = Dockerfile(parser.specs)
# df.save('path/to/Dockerfile')
# print(df)

# Build image.
image = DockerImage(df).build(log_console=False, log_filepath="build.log")

# Start container, and run commands.
container = DockerContainer(image).start()
container.exec_run('python -c "import nipype; print(nipype.__version__)"')
# Returns '0.13.0-dev\n'
container.exec_run('ANTS')
# Returns ' call ANTS -h or ANTS --help \n'
container.cleanup(remove=True)
```

The example above creates this Dockerfile:

```dockerfile
FROM ubuntu:17.04

ARG DEBIAN_FRONTEND=noninteractive

#----------------------------
# Install common dependencies
#----------------------------
RUN apt-get update -qq && apt-get install -yq --no-install-recommends bzip2 ca-certificates curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#-------------------------------------------------
# Install Miniconda, and set up Python environment
#-------------------------------------------------
ENV PATH=/opt/miniconda/envs/default/bin:$PATH
RUN curl -ssL -o miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash miniconda.sh -b -p /opt/miniconda \
    && rm -f miniconda.sh \
    && /opt/miniconda/bin/conda config --add channels conda-forge \
    && /opt/miniconda/bin/conda create -y -q -n default python=3.5.1 \
    	traits \
    && conda clean -y --all \
    && pip install -U -q --no-cache-dir pip \
    && pip install -q --no-cache-dir \
    	https://github.com/nipy/nipype/archive/master.tar.gz \
    && rm -rf /opt/miniconda/[!envs]*

#-------------------
# Install ANTs 2.1.0
#-------------------
WORKDIR /opt
RUN URL=https://www.dropbox.com/s/x7eyk125bhwiisu/ants-2.1.0_centos-5.tar.gz?dl=1 \
    && curl -sSL $URL | tar zx
ENV ANTSPATH=/opt/ants \
    PATH=/opt/ants:$PATH

#------------------
# Install FSL 5.0.10
#------------------
RUN curl -sSL https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-5.0.10-centos6_64.tar.gz \
    | tar zx -C /opt \
    && cp /opt/fsl/etc/fslconf/fsl.sh /etc/profile.d/ \
    && FSLPYFILE=/opt/fsl/etc/fslconf/fslpython_install.sh \
    && [ -f $FSLPYFILE ] && $FSLPYFILE -f /opt/fsl -q || true
ENV FSLDIR=/opt/fsl \
    PATH=/opt/fsl/bin:$PATH

#----------------------
# Install MCR and SPM12
#----------------------
# Install required libraries
RUN apt-get update -qq && apt-get install -yq --no-install-recommends libxext6 libxt6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install MATLAB Compiler Runtime
WORKDIR /opt
RUN curl -sSL -o mcr.zip https://www.mathworks.com/supportfiles/downloads/R2017a/deployment_files/R2017a/installers/glnxa64/MCR_R2017a_glnxa64_installer.zip \
    && unzip -q mcr.zip -d mcrtmp \
    && mcrtmp/install -destinationFolder /opt/mcr -mode silent -agreeToLicense yes \
    && rm -rf mcrtmp mcr.zip /tmp/*

# Install standalone SPM
WORKDIR /opt
RUN curl -sSL -o spm.zip http://www.fil.ion.ucl.ac.uk/spm/download/restricted/utopia/dev/spm12_latest_Linux_R2017a.zip \
    && unzip -q spm.zip \
    && rm -rf spm.zip
ENV MATLABCMD=/opt/mcr/v*/toolbox/matlab \
    SPMMCRCMD="/opt/spm*/run_spm*.sh /opt/mcr/v*/ script" \
    FORCE_SPMMCR=1 \
    LD_LIBRARY_PATH=/opt/mcr/v*/runtime/glnxa64:/opt/mcr/v*/bin/glnxa64:/opt/mcr/v*/sys/os/glnxa64:$LD_LIBRARY_PATH
```
