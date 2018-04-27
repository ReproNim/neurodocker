#!/bin/sh

set -e

# Generate Dockerfile.
generate_docker() {
  docker run --rm kaczmarj/neurodocker:master generate docker \
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
    --cmd jupyter-notebook
}

# Generate Singularity recipe (does not include last --cmd arg)
generate_singularity() {
  docker run --rm kaczmarj/neurodocker:master generate singularity \
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
    --workdir /home/neuro
}

generate_docker > Dockerfile
generate_singularity > Singularity
