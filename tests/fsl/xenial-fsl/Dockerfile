FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    bzip2 \
    ca-certificates \
    curl \
    # FSL dependencies.
    libexpat1-dev \
    libgl1-mesa-dev \
    libx11-dev \
    zlib1g-dev

ENV FSL_VERSION=5.0.8 \
    BASE_URL=https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions/ \
    DOWNLOAD_DIR=/root/fslbuild
# These environment variables depend on ones defined above.
# See https://github.com/docker/docker/pull/10431
ENV FSLDIR=$DOWNLOAD_DIR/fsl \
    TARBALL=fsl-$FSL_VERSION-sources.tar.gz

# Download and extract source.
RUN mkdir $DOWNLOAD_DIR && cd $DOWNLOAD_DIR && \
    curl -LO ${BASE_URL}${TARBALL} && \
    tar zxf ${TARBALL} && \
    rm ${TARBALL}

# Uncomment lines pertaining to vars FSLMACHTYPE and FSLCONFDIR.
# The -i flag makes the changes in-place.
RUN sed -i '/FSLMACHTYPE/s/^#//g' ${FSLDIR}/etc/fslconf/fsl.sh && \
    sed -i '/FSLCONFDIR/s/^#//g' ${FSLDIR}/etc/fslconf/fsl.sh && \
    # How could we do automate this part? $FSLMACHTYPE is linux_64-gcc4.4 in
    # this case, so the `cp` command fails.
    # cp -r $FSLDIR/config/linux_64-gcc4.4 $FSLDIR/config/$FSLMACHTYPE && \
    # Symlink install and ginstall. Some FSL build functions look for ginstall.
    ln -s /usr/bin/install /usr/bin/ginstall

# Build source.
WORKDIR $FSLDIR
RUN ./build

# Add FSLDIR to PATH.
ENV PATH $FSLDIR/bin:$PATH

# Change working directory to / ?
