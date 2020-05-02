#!/bin/sh

set -e

# Generate Dockerfile or Singularity recipe.
generate() {
  docker run --rm repronim/neurodocker:master generate "$1" \
    --base=neurodebian:stretch-non-free \
    --pkg-manager=apt \
    --install fsl vim emacs-nox \
    --add-to-entrypoint='source /etc/fsl/fsl.sh' \
    --user=neuro \
    --workdir='/home/neuro'
}

generate docker > Dockerfile
generate singularity > Singularity
