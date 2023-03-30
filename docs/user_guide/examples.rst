Examples
========

This page includes examples of using Neurodocker to build containers with popular
neuroimaging packages. The commands generate Dockerfiles. To generate Singularity
recipes, simply replace

.. code-block:: bash

    neurodocker generate docker

with

.. code-block:: bash

    neurodocker generate singularity


To see the options for each package, please run

.. code-block:: bash

    neurodocker generate docker --help

or

.. code-block:: bash

    neurodocker generate singularity --help


.. note ::

    Neurodocker is meant to create command-line environments. At the moment, graphical
    user interfaces (like FreeView and FSLEyes) are not installed properly. It is
    possible that this will change in the future.


FSL
---

.. _fsl_docker:

Docker
~~~~~~

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --fsl version=6.0.4 \
    > fsl604.Dockerfile

    docker build --tag fsl:6.0.4 --file fsl604.Dockerfile .

    # Run fsl's bet program.
    docker run --rm -it fsl:6.0.4 bet

AFNI
----

.. _afni_docker:

Docker
~~~~~~

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager yum \
        --base-image fedora:35 \
        --afni method=binaries version=latest \
    > afni-binaries.Dockerfile

    docker build --tag afni:latest --file afni-binaries.Dockerfile .

This does not install AFNI's R packages. To install relevant R things, use the following:


.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image fedora:35 \
        --afni method=binaries version=latest install_r_pkgs=true \
    > afni-binaries-r.Dockerfile

    docker build --tag afni:latest-with-r --file afni-binaries-r.Dockerfile .


One can also build AFNI from source. The code below builds the current master branch.
Beware that this is AFNI's bleeding edge!

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image fedora:35 \
        --afni method=source version=master \
    > afni-source.Dockerfile

    docker build --tag afni:master --file afni-source.Dockerfile .

FreeSurfer
----------

.. _freesurfer_docker:


Docker
~~~~~~

The FreeSurfer installation is several gigabytes in size, but sometimes, users just
the pieces for :code:`recon-all`. For this reason, Neurodocker provides a FreeSurfer
minified for :code:`recon-all`.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --freesurfer version=7.1.1-min \
    > freesurfer7-min.Dockerfile

    docker build --tag freesurfer:7.1.1-min --file freesurfer7-min.Dockerfile .

ANTS
----

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --ants version=2.3.4 \
    > ants-234.Dockerfile

    docker build --tag ants:2.3.4 --file ants-234.Dockerfile .



CAT12
---

CAT12 requires the MCR in the correction version. Miniconda and nipype is optional but recommended to use CAT12 from NiPype.

.. code-block:: bash

    neurodocker generate docker \
        --base-image ubuntu:16.04 \
        --pkg-manager apt \
        --mcr 2017b \
        --cat12 version=r1933_R2017b \
        --miniconda \
         version=latest \
         conda_install='python=3.8 traits nipype numpy scipy h5py scikit-image' \
    > cat12-r1933_R2017b.Dockerfile

    docker build --tag cat12:r1933_R2017b --file cat12-r1933_R2017b.Dockerfile .

SPM
---

.. note::

    Due to the version of the Matlab Compiler Runtime used, SPM12 should be used with
    a Debian Stretch base image.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:stretch-slim \
        --spm12 version=r7771 \
    > spm12-r7771.Dockerfile

    docker build --tag spm12:r7771 --file spm12-r7771.Dockerfile .


Miniconda
---------

Docker with new :code:`conda` environment, python packages installed with :code:`conda` and :code:`pip`.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --miniconda \
            version=latest \
            env_name=env_scipy \
            env_exists=false \
            conda_install=pandas \
            pip_install=scipy \
    > conda-env.Dockerfile

    docker build --tag conda-env --file conda-env.Dockerfile .


Nipype tutorial
---------------

.. _nipype_tutorial_docker:

Docker
~~~~~~

.. code-block:: bash

    neurodocker generate docker \
    --pkg-manager apt \
    --base-image neurodebian:stretch-non-free \
    --arg DEBIAN_FRONTEND=noninteractive \
    --install convert3d ants fsl gcc g++ graphviz tree \
            git-annex-standalone vim emacs-nox nano less ncdu \
            tig git-annex-remote-rclone octave netbase \
    --spm12 version=r7771 \
    --miniconda \
    version=latest \
    conda_install="python=3.8 pytest jupyter jupyterlab jupyter_contrib_nbextensions
                    traits pandas matplotlib scikit-learn scikit-image seaborn nbformat
                    nb_conda" \
    pip_install="https://github.com/nipy/nipype/tarball/master
                    https://github.com/INCF/pybids/tarball/master
                    nilearn datalad[full] nipy duecredit nbval" \
    --run 'jupyter nbextension enable exercise2/main && jupyter nbextension enable spellchecker/main' \
    --run 'mkdir /data && chmod 777 /data && chmod a+s /data' \
    --run 'mkdir /output && chmod 777 /output && chmod a+s /output' \
    --user neuro \
    --run-bash 'cd /data
    && datalad install -r ///workshops/nih-2017/ds000114
    && cd ds000114
    && datalad update -r
    && datalad get -r sub-01/ses-test/anat sub-01/ses-test/func/*fingerfootlips*' \
    --run 'curl -fL https://files.osf.io/v1/resources/fvuh8/providers/osfstorage/580705089ad5a101f17944a9 -o /data/ds000114/derivatives/fmriprep/mni_icbm152_nlin_asym_09c.tar.gz
    && tar xf /data/ds000114/derivatives/fmriprep/mni_icbm152_nlin_asym_09c.tar.gz -C /data/ds000114/derivatives/fmriprep/.
    && rm /data/ds000114/derivatives/fmriprep/mni_icbm152_nlin_asym_09c.tar.gz
    && find /data/ds000114/derivatives/fmriprep/mni_icbm152_nlin_asym_09c -type f -not -name ?mm_T1.nii.gz -not -name ?mm_brainmask.nii.gz -not -name ?mm_tpm*.nii.gz -delete' \
    --copy . "/home/neuro/nipype_tutorial" \
    --user root \
    --run 'chown -R neuro /home/neuro/nipype_tutorial' \
    --run 'rm -rf /opt/conda/pkgs/*' \
    --user neuro \
    --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
    --workdir /home/neuro/nipype_tutorial \
    --entrypoint jupyter-notebook \
    > nipype-tutorial.Dockerfile

    docker build --tag nipype-tutorial .
