#!/bin/bash

docker run --rm kaczmarj/neurodocker:master generate -b neurodebian:stretch-non-free -p apt \
--install vim emacs-nox \
--user=neuro \
--miniconda \
  conda_install="python=3.6 jupyter jupyterlab jupyter_contrib_nbextensions 
                 matplotlib scikit-learn seaborn" \
  pip_install="nilearn" \
  env_name="neuro_py36" \
  activate=True \
--run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
--user=root \
--run 'chown -R neuro /home/neuro' \
--user=neuro \
--workdir /home/neuro \
--cmd "jupyter-notebook" \
--no-check-urls > Dockerfile