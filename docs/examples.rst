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
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --afni method=binaries version=latest \
    > afni-binaries.Dockerfile

    docker build --tag afni:latest --file afni-binaries.Dockerfile .

This does not install AFNI's R packages. To install relevant R things, use the following:


.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --afni method=binaries version=latest install_r_pkgs=true \
    > afni-binaries-r.Dockerfile

    docker build --tag afni:latest-with-r --file afni-binaries-r.Dockerfile .


One can also build AFNI from source. The code below builds the current master branch.
Beware that this is AFNI's bleeding edge!

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
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

.. todo::

    Add an example of building a Miniconda image.
