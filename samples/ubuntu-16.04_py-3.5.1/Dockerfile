FROM ubuntu:16.04

# Get dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl

# Install Miniconda, and create Conda environment from file.
RUN curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/miniconda  && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV CONDAPATH=/usr/local/miniconda/bin \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
COPY conda-env.json /home/conda-env.json
RUN $CONDAPATH/conda update -y conda && \
    $CONDAPATH/conda env create -f /home/conda-env.json -n new_env && \
    cd $CONDAPATH/../ && rm -rf conda-meta include share ssl && \
    $CONDAPATH/conda clean -y -a
ENV PATH=/usr/local/miniconda/envs/new_env/bin:$PATH