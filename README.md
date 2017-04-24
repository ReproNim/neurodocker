# neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates Docker images with specified versions of Python and neuroimaging software. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces. See the [example](#example) at the bottom of this page.



## Supported Software

This list is growing.

### ANTs

To install, include `'ants'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'ants'` are keywords for [`neurodocker.interfaces.ANTs`](neurodocker/interfaces/ants.py#L27). Binaries can be installed (compiled on CentOS 5), or ANTs can be compiled from source.

### Conda

To install, include `'conda_env'` in the specifications dictionary. Valid keys within `'conda_env'` are keywords for [`neurodocker.interfaces.Miniconda`](neurodocker/interfaces/miniconda.py#L12). The `conda-forge` channel is added by default.

### FSL

To install, include `'fsl'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'fsl'` are keywords for [`neurodocker.interfaces.FSL`](neurodocker/interfaces/fsl.py#L11). Beware that FSL's Python installer will panic if used on a Debian-based system.

### SPM

To install, include `'spm'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'spm'` are keywords for [`neurodocker.interfaces.SPM`](neurodocker/interfaces/spm.py#L17). Currently, only SPM12 and MATLAB R2017a are supported.



## Example


In the following example, a dictionary of specifications is used to generate a Dockerfile. The resulting Docker image contains Python 3.5.1, Nipype, and ANTs 2.1.0.


```python
from neurodocker import (DockerContainer, Dockerfile, DockerImage,
                         SpecsParser)
# Specify the environment.
specs = {
    'base': 'ubuntu:16.04',
    'conda_env': {
        'python_version': '3.5.1',
        'conda_install': ['traits'],
        'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz']
    },
    'software': {
        'ants': {'version': '2.1.0', 'use_binaries': True},
        'fsl': {'version': '5.0.8', 'use_binaries': True},
        'spm': {'version': '12', 'matlab_version': 'R2017a'}
    }
}
# Generate the Dockerfile.
parser = SpecsParser(specs=specs)
df = Dockerfile(parser.specs, pkg_manager='apt')

# Build the image from the Dockerfile.
image = DockerImage(fileobj=df.cmd).build()

# Start up the container, run commands, and stop+remove container.
container = DockerContainer(img).start()
container.exec_run('python -c "import nipype; print(nipype.__version__)"')
# Returns '0.13.0-dev\n'
container.exec_run('ANTS')
# Returns ' call ANTS -h or ANTS --help \n'
container.cleanup(remove=True, force=True)
```

Here is the content of the Dockerfile in the example above:

```dockerfile
FROM ubuntu:16.04

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
WORKDIR /opt
RUN curl -ssL -o miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash miniconda.sh -b -p /opt/miniconda \
    && rm -f miniconda.sh
RUN /opt/miniconda/bin/conda config --add channels conda-forge \
    && /opt/miniconda/bin/conda create -y -q -n default python=3.5.1 traits
ENV PATH=/opt/miniconda/envs/default/bin:$PATH
RUN pip install --upgrade -q --no-cache-dir pip
&& pip install -q --no-cache-dir https://github.com/nipy/nipype/archive/master.tar.gz \
    && conda clean -y --all \
    && cd /opt/miniconda \
    && rm -rf bin conda-meta include lib pkgs share ssl

#-------------------
# Install ANTs 2.1.0
#-------------------
WORKDIR /opt
RUN URL=https://www.dropbox.com/s/x7eyk125bhwiisu/ants-2.1.0_centos-5.tar.gz?dl=1 \
    && curl -sSL $URL | tar zx
ENV ANTSPATH=/opt/ants \
    PATH=/opt/ants:$PATH

#------------------
# Install FSL 5.0.8
#------------------
WORKDIR /opt
ENV SHELL='bash'
RUN curl -sSL https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions/fsl-5.0.8-centos5_64.tar.gz | tar zx \
    && cp fsl/etc/fslconf/fsl.sh /etc/profile.d/
ENV FSLDIR=/opt/fsl \
    PATH=/opt/fsl/bin:$PATH

#----------------------
# Install MCR and SPM12
#----------------------
# Install required libraries
RUN apt-get update -qq && apt-get install -yq --no-install-recommends libxext6 libxt6

# Install MATLAB Compiler Runtime
WORKDIR /opt
RUN echo "destinationFolder=/opt/mcr" > mcr_options.txt \
    && echo "agreeToLicense=yes" >> mcr_options.txt \
    && echo "outputFile=/tmp/matlabinstall_log" >> mcr_options.txt \
    && echo "mode=silent" >> mcr_options.txt \
    && mkdir -p matlab_installer \
    && curl -sSL -o matlab_installer/installer.zip https://www.mathworks.com/supportfiles/downloads/R2017a/deployment_files/R2017a/installers/glnxa64/MCR_R2017a_glnxa64_installer.zip \
    && unzip matlab_installer/installer.zip -d matlab_installer/ \
    && matlab_installer/install -inputFile /opt/mcr_options.txt \
    && rm -rf matlab_installer mcr_options.txt

# Install standalone SPM
WORKDIR /opt
RUN curl -sSL -o spm12.zip http://www.fil.ion.ucl.ac.uk/spm/download/restricted/utopia/dev/spm12_latest_Linux_R2017a.zip \
    && unzip spm12.zip \
    && rm -rf spm12.zip /tmp/*
ENV MATLABCMD="/opt/mcr/v92/toolbox/matlab" \
    SPMMCRCMD="/opt/spm12/run_spm12.sh /opt/mcr/v92/ script" \
    FORCE_SPMMCR=1 \
    LD_LIBRARY_PATH=/opt/mcr/v92/runtime/glnxa64:/opt/mcr/v92/bin/glnxa64:/opt/mcr/v92/sys/os/glnxa64:$LD_LIBRARY_PATH
```
