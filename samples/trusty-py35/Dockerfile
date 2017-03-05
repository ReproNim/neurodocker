FROM ubuntu:14.04

RUN apt-get update && apt-get install -yq \
    --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl \
    wget \
    xvfb

# Install miniconda.
RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda2-latest-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda2-latest-Linux-x86_64.sh
# Define environment variables.
ENV PATH=/usr/local/miniconda/bin:$PATH \
    PYTHONPATH=/usr/local/miniconda/lib/python2.7/site-packages \
    PYTHONNOUSERSITE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
# Install Python 2.7.
RUN conda install python=2.7

# Install Python packages.
RUN conda config --add channels conda-forge && \
    conda install -y numpy==1.11