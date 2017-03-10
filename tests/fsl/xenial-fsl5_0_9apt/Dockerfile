# This Dockerfile is based on the one for fmripep
# (https://github.com/poldracklab/fmriprep/blob/master/Dockerfile).
FROM ubuntu:xenial-20170214

RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl

# Get NeuroDebian.
ENV NEURODEBIAN_URL http://neuro.debian.net/lists/xenial.us-nh.full
RUN curl -sSl $NEURODEBIAN_URL >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key adv --recv-keys --keyserver hkp://pgp.mit.edu:80 0xA5D32F012649A5A9 && \
    apt-get update

RUN apt-get install -y fsl-core
