#!/bin/sh

set -e

# Generate Dockerfile
generate_docker() {
  docker run --rm kaczmarj/neurodocker:master generate docker \
  --base neurodebian:stretch-non-free \
  --pkg-manager apt \
  --install convert3d ants fsl gcc g++ graphviz tree \
            git-annex-standalone vim emacs-nox nano less ncdu \
            tig git-annex-remote-rclone \
  --add-to-entrypoint "source /etc/fsl/fsl.sh" \
  --spm12 version=r7219 \
  --user=neuro \
  --miniconda \
    conda_install="python=3.6 jupyter jupyterlab jupyter_contrib_nbextensions
                   traits pandas matplotlib scikit-learn seaborn" \
    pip_install="https://github.com/nipy/nipype/tarball/master
                 https://github.com/INCF/pybids/tarball/master
                 nilearn datalad[full] nipy duecredit" \
    create_env="neuro" \
    activate=true \
  --run-bash 'source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable spellchecker/main' \
  --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = "0.0.0.0" > ~/.jupyter/jupyter_notebook_config.py' \
  --user=root \
  --run 'mkdir /data && chmod 777 /data && chmod a+s /data' \
  --run 'mkdir /output && chmod 777 /output && chmod a+s /output' \
  --user=neuro \
  --run-bash 'source activate neuro
    && cd /data
    && datalad install -r ///workshops/nih-2017/ds000114
    && cd /data/ds000114
    && datalad get -r -J4 sub-*/ses-test/anat
    && datalad get -r -J4 sub-*/ses-test/func/*fingerfootlips*
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*space-mni152nlin2009casym_preproc.nii.gz
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*t1w_preproc.nii.gz
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*h5
    && datalad get -r -J4 derivatives/freesurfer/sub-01' \
  --run 'curl -fsSL https://files.osf.io/v1/resources/fvuh8/providers/osfstorage/580705089ad5a101f17944a9 \
    | tar xz -C /data/ds000114/derivatives/fmriprep' \
  --copy . "/home/neuro/nipype_tutorial" \
  --workdir /home/neuro \
  --cmd jupyter-notebook
}


# Generate Singularity file (does not include last --cmd option)
generate_singularity() {
  docker run --rm kaczmarj/neurodocker:master generate singularity \
  --base neurodebian:stretch-non-free \
  --pkg-manager apt \
  --install convert3d ants fsl gcc g++ graphviz tree \
            git-annex-standalone vim emacs-nox nano less ncdu \
            tig git-annex-remote-rclone \
  --add-to-entrypoint "source /etc/fsl/fsl.sh" \
  --spm12 version=r7219 \
  --user=neuro \
  --miniconda \
    conda_install="python=3.6 jupyter jupyterlab jupyter_contrib_nbextensions
                   traits pandas matplotlib scikit-learn seaborn" \
    pip_install="https://github.com/nipy/nipype/tarball/master
                 https://github.com/INCF/pybids/tarball/master
                 nilearn datalad[full] nipy duecredit" \
    create_env="neuro" \
    activate=true \
  --run-bash 'source activate neuro && jupyter nbextension enable exercise2/main && jupyter nbextension enable spellchecker/main' \
  --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = "0.0.0.0" > ~/.jupyter/jupyter_notebook_config.py' \
  --user=root \
  --run 'mkdir /data && chmod 777 /data && chmod a+s /data' \
  --run 'mkdir /output && chmod 777 /output && chmod a+s /output' \
  --user=neuro \
  --run-bash 'source activate neuro
    && cd /data
    && datalad install -r ///workshops/nih-2017/ds000114
    && cd /data/ds000114
    && datalad get -r -J4 sub-*/ses-test/anat
    && datalad get -r -J4 sub-*/ses-test/func/*fingerfootlips*
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*space-mni152nlin2009casym_preproc.nii.gz
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*t1w_preproc.nii.gz
    && datalad get -r -J4 derivatives/fmriprep/sub-*/anat/*h5
    && datalad get -r -J4 derivatives/freesurfer/sub-01' \
  --run 'curl -fsSL https://files.osf.io/v1/resources/fvuh8/providers/osfstorage/580705089ad5a101f17944a9 \
    | tar xz -C /data/ds000114/derivatives/fmriprep' \
  --copy . "/home/neuro/nipype_tutorial" \
  --workdir /home/neuro
}

generate_docker > Dockerfile
generate_singularity > Singularity
