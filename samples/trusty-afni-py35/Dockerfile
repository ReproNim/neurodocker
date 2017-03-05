FROM ubuntu:14.04

RUN apt-get update && apt-get install -yq \
    --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl \
    xvfb

# Install AFNI dependencies.
RUN apt-get -y -qq install libxp6 libglu1-mesa gsl-bin libjpeg62-dev libxft-dev
# Install AFNI.
RUN curl -L https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz | tar zxC /usr/local && \
    mv /usr/local/linux_openmp_64 /usr/local/afni
ENV PATH $PATH:/usr/local/afni

# Install miniconda.
RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-latest-Linux-x86_64.sh
# Define environment variables.
ENV PATH=/usr/local/miniconda/bin:$PATH \
    PYTHONPATH=/usr/local/miniconda/lib/python3.5/site-packages \
    PYTHONNOUSERSITE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
# Install Python 3.5.1.
RUN conda install python=3.5.1

# Install Python packages.
RUN conda config --add channels conda-forge && \
    conda install -y nipype==0.12

RUN pip install pybids

FROM ubuntu:14.04

RUN apt-get update && apt-get install -yq \
    --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl \
    xvfb

# Install AFNI dependencies.
RUN apt-get -y -qq install libxp6 libglu1-mesa gsl-bin libjpeg62-dev libxft-dev
# Install AFNI.
RUN curl -L https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz | tar zxC /usr/local && \
    mv /usr/local/linux_openmp_64 /usr/local/afni
ENV PATH $PATH:/usr/local/afni

# Install miniconda.
RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-latest-Linux-x86_64.sh
# Define environment variables.
ENV PATH=/usr/local/miniconda/bin:$PATH \
    PYTHONPATH=/usr/local/miniconda/lib/python3.5/site-packages \
    PYTHONNOUSERSITE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
# Install Python 3.5.1.
RUN conda install python=3.5.1

# Install Python packages.
RUN conda config --add channels conda-forge && \
    conda install -y nipype==0.12

RUN pip install pybids