#!/bin/sh

set -e

# Generate Dockerfile or Singularity recipe.
generate() {
  docker run --rm kaczmarj/neurodocker:master generate "$1" \
    --base=neurodebian:stretch-non-free \
    --pkg-manager=apt \
    --install vim emacs-nox \
    --user=neuro \
    --miniconda \
      conda_install="python=3.6 jupyter jupyterlab jupyter_contrib_nbextensions
                     matplotlib scikit-learn seaborn" \
      pip_install="nilearn" \
      env_name="neuro_py36" \
      activate=true \
    --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
    --workdir /home/neuro \
    --entrypoint "/neurodocker/startup.sh jupyter-notebook"
}

generate docker > Dockerfile
generate singularity > Singularity
