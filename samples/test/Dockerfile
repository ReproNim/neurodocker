FROM ubuntu:16.04

RUN apt-get update && apt-get install -y bzip2 curl

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
# Install Python 3.5.
RUN conda install python=3.5

# Install Python packages.
RUN conda config --add channels conda-forge && \
    conda install -y nipype==0.12 numpy
