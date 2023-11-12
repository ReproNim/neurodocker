Examples
========

This page includes examples of using Neurodocker to build containers with popular
neuroimaging packages.

Supported software
------------------

.. INSERT LIST START (will be updated automatically in ci)

- `afni <https://afni.nimh.nih.gov>`_
- `ants <http://stnava.github.io/ANTs/>`_
- `cat12 <https://neuro-jena.github.io/cat/>`_
- `convert3d <http://www.itksnap.org/pmwiki/pmwiki.php?n=Convert3D.Convert3D>`_
- `dcm2niix <https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage>`_
- `freesurfer <https://surfer.nmr.mgh.harvard.edu/>`_
- `fsl <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/>`_
- `jq <https://jqlang.github.io/jq/>`_
- `matlabmcr <https://www.mathworks.com/products/compiler/matlab-runtime.html>`_
- `minc <https://github.com/BIC-MNI/minc-toolkit-v2>`_
- `miniconda <https://docs.conda.io/projects/miniconda/en/latest/>`_
- `mricron <https://github.com/neurolabusc/MRIcron>`_
- `mrtrix3 <https://www.mrtrix.org/>`_
- `ndfreeze <https://neuro.debian.net/pkgs/neurodebian-freeze.html>`_
- `neurodebian <http://neuro.debian.net>`_
- `niftyreg <https://github.com/KCL-BMEIS/niftyreg>`_
- `petpvc <https://github.com/UCL/PETPVC>`_
- `spm12 <https://www.fil.ion.ucl.ac.uk/spm/>`_
- `vnc <https://www.realvnc.com/>`_

.. INSERT LIST END

The commands generate Dockerfiles. To generate Singularity
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
        --base-image debian:bullseye-slim \
        --fsl version=6.0.7.1 \
    > fsl6071.Dockerfile

    docker build --tag fsl:6.0.7.1 --file fsl6071.Dockerfile .

This will ask the following question interactively:

.. code-block:: bash

    FSL is non-free. If you are considering commercial use of FSL, please consult the relevant license(s). Proceed? [y/N]

If you are using neurodocker non-interactively, this problem can be avoided using:

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --yes \
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
        --base-image fedora:36 \
        --afni method=binaries version=latest \
    > afni-binaries.Dockerfile

    docker build --tag afni:latest --file afni-binaries.Dockerfile .

This does not install AFNI's R packages. To install relevant R things, use the following:


.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager yum \
        --base-image fedora:36 \
        --afni method=binaries version=latest install_r_pkgs=true \
    > afni-binaries-r.Dockerfile

    docker build --tag afni:latest-with-r --file afni-binaries-r.Dockerfile .

.. todo::

    Building AFNI from source is currently failing on most tested distributions.

.. https://github.com/ReproNim/neurodocker/blob/test_docker_build/docs/README.md#afni

.. One can also build AFNI from source. The code below builds the current master branch.
.. Beware that this is AFNI's bleeding edge!

.. .. code-block:: bash

..     neurodocker generate docker \
..         --pkg-manager yum \
..         --base-image fedora:36 \
..         --afni method=source version=master \
..     > afni-source.Dockerfile

..     docker build --tag afni:master --file afni-source.Dockerfile .

FreeSurfer
----------

.. _freesurfer_docker:


Docker
~~~~~~

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:bullseye-slim \
        --freesurfer version=7.4.1 \
    > freesurfer741.Dockerfile

    docker build --tag freesurfer:7.4.1 --file freesurfer741.Dockerfile .

.. todo::

    The minified version on Freesurfer currently fails to build on all tested distributions.

.. https://github.com/ReproNim/neurodocker/blob/test_docker_build/docs/README.md#freesurfer

.. The FreeSurfer installation is several gigabytes in size, but sometimes, users just
.. the pieces for :code:`recon-all`. For this reason, Neurodocker provides a FreeSurfer
.. minified for :code:`recon-all`.

ANTS
----

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:bullseye-slim \
        --ants version=2.4.3 \
    > ants-234.Dockerfile

    docker build --tag ants:2.4.3 --file ants-243.Dockerfile .

.. note::

    Building docker images of ANTS from source fails on most tested distributions.

.. https://github.com/ReproNim/neurodocker/blob/test_docker_build/docs/README.md#ants

CAT12
-----

CAT12 requires the MCR in the correction version.
Miniconda and nipype is optional but recommended to use CAT12 from NiPype.

.. code-block:: bash

    neurodocker generate docker \
        --base-image ubuntu:22.04 \
        --pkg-manager apt \
        --mcr 2017b \
        --cat12 version=r2166_R2017b \
        --miniconda \
         version=latest \
         conda_install='python=3.11 traits nipype numpy scipy h5py scikit-image' \
    > cat12-r2166_R2017b.Dockerfile

    docker build --tag cat12:r2166_R2017b --file cat12-r2166_R2017b.Dockerfile .

SPM
---

..     Due to the version of the Matlab Compiler Runtime used,
..     SPM12 should be used with a Debian Stretch base image.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image centos:7 \
        --spm12 version=r7771 \
    > spm12-r7771.Dockerfile

    docker build --tag spm12:r7771 --file spm12-r7771.Dockerfile .

.. note::

    Building docker images of SPM12 from source fails on most tested distributions.

.. https://github.com/ReproNim/neurodocker/blob/test_docker_build/docs/README.md#spm12

Miniconda
---------

Docker with new :code:`conda` environment, python packages installed with :code:`conda` and :code:`pip`.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:bullseye-slim \
        --miniconda \
            version=latest \
            env_name=env_scipy \
            env_exists=false \
            conda_install=pandas \
            pip_install=scipy \
    > conda-env.Dockerfile

    docker build --tag conda-env --file conda-env.Dockerfile .


.. Nipype tutorial
.. ---------------

.. .. _nipype_tutorial_docker:

Docker
~~~~~~

.. literalinclude:: examples/nipype_tuto.txt
