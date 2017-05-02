# neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates Docker images with specified versions of Python and neuroimaging software. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces. See the [example](#example) at the bottom of this page.



## Supported Software

This list is growing.

### ANTs

To install, include `'ants'` (case-insensitive) in the specifications dictionary. Valid keys within `'ants'` are keywords for [`neurodocker.interfaces.ANTs`](neurodocker/interfaces/ants.py#L27). Pre-compiled binaries can be installed, or ANTs can be compiled from source.

### Conda

To install, include `'miniconda'` (case-insensitive) in the specifications dictionary. Valid keys within `'miniconda'` are keywords for [`neurodocker.interfaces.Miniconda`](neurodocker/interfaces/miniconda.py#L12). The `conda-forge` channel is added by default.

### FSL

To install, include `'fsl'` (case-insensitive) in the specifications dictionary. Valid keys within `'fsl'` are keywords for [`neurodocker.interfaces.FSL`](neurodocker/interfaces/fsl.py#L11). Beware that FSL's Python installer will panic if used on a Debian-based system.

### SPM

To install, include `'spm'` (case-insensitive) in the specifications dictionary. Valid keys within `'spm'` are keywords for [`neurodocker.interfaces.SPM`](neurodocker/interfaces/spm.py#L17). Currently, only SPM12 and MATLAB R2017a are supported.



## Example


In the following example, a dictionary of specifications is used to generate a Dockerfile. A Docker image is built from the string representation of the Dockerfile. A container is started from that container, and commands are run within the running container. When finished, the container is stopped and removed.


```python
from neurodocker import Dockerfile, DockerImage, DockerContainer, SpecsParser

specs = {
    'base': 'ubuntu:17.04',
    'pkg_manager': 'apt',
    'check_urls': True,  # Verify communication with URLs used in build.
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
# df.save('path/to/this/Dockerfile')
# print(df)

image = DockerImage(df).build()

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
WORKDIR /opt
RUN curl -ssL -o miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash miniconda.sh -b -p /opt/miniconda \
    && rm -f miniconda.sh
RUN /opt/miniconda/bin/conda config --add channels conda-forge \
    && /opt/miniconda/bin/conda create -y -q -n default python=3.5.1 traits
ENV PATH=/opt/miniconda/envs/default/bin:$PATH
RUN pip install --upgrade -q --no-cache-dir pip \
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
