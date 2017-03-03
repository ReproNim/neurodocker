FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    curl \
    bzip2

# Install miniconda.
RUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/miniconda && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/usr/local/miniconda/bin:$PATH \
    PYTHONNOUSERSITE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
RUN conda install python=3.5.1

# Install conda packages.
RUN conda config --add channels conda-forge && \
    conda install -y numpy==1.10 scipy