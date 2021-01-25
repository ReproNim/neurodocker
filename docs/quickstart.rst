Quickstart
==========

Install
-------

The recommended approach is to install :code:`neurodocker` in a virtual environment.
Create one with :code:`conda`, :code:`venv`, or another virtual environment provider,
and then run the following:

.. code-block::

    python -m pip install neurodocker

Generate a container
--------------------

Use the command :code:`neurodocker generate` to generate containers. In the examples below,
we generate containers with `Nipype <https://nipype.readthedocs.io/en/latest/>`_,
`Jupyter Notebook <https://jupyter.org/>`_, and `ANTs <https://github.com/ANTsX/ANTs>`_.

Please see the :doc:`examples` page for more.

Docker
~~~~~~

Run the following code snippet to generate a `Dockerfile <https://docs.docker.com/engine/reference/builder/>`_.
This is a file that defines how to build a Docker image.

(This requires having `Docker <https://docs.docker.com/get-docker/>`_ installed)

.. code-block::

    neurodocker generate docker --pkg-manager apt \
        --base-image neurodebian:buster \
        --ants version=2.3.4 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot

You should see a block of text appear in the console. This is the Dockerfile generated
by *Neurodocker*. Instructions in the Dockerfile are ordered in the same way as the
arguments in the command-line. To build a Docker image with this, save the output to a
file in an empty directory, and build with :code:`docker build`:

.. code-block::

    mkdir docker-example
    cd docker-example
    neurodocker generate docker --pkg-manager apt \
        --base-image neurodebian:buster \
        --ants version=2.3.4 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot > Dockerfile
    docker build --tag nipype-ants .

Then, you can start a Jupyter Notebook with the following command. This will mount
the current working directory to :code:`work` within the container, so any files you
create in this directory are saved. If we had not mounted this directory, all of the files
created in :code:`/work` would be gone after the container was stopped.

.. code-block::

    docker run --rm -it --workdir /work --volume $PWD:/work --publish 8888:8888 \
        nipype-ants jupyter-notebook --ip 0.0.0.0 --port 8888

Feel free to create a new notebook and :code:`import nipype`.

Singularity
~~~~~~~~~~~

The only difference between this command and the one above is :code:`neurodocker generate singularity`
versus :code:`neurodocker generate docker`. This will be the case when generating the
majority of containers. The code block below generates a
`Singularity definition file <https://sylabs.io/guides/3.7/user-guide/definition_files.html>`_.
This file can be used to create a Singularity container.

(This requires having `Singularity <https://sylabs.io/guides/3.7/user-guide/quick_start.html>`_ installed.

.. code-block::

    neurodocker generate singularity --pkg-manager apt \
        --base-image neurodebian:buster \
        --ants version=2.3.4 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot

You should see a block of text appear in the console. This is the Singularity definition.
To build the Singularity image, create a new directory, save this output to a file, and
use :code:`sudo singularity build`. Note that this requires superuser privileges. You
will not be able to run this on a shared computing environment, like a high performance cluster.

.. code-block::

    mkdir singularity-example
    cd singularity-example
    neurodocker generate singularity --pkg-manager apt \
        --base-image neurodebian:buster \
        --ants version=2.3.4 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot > Singularity
    sudo singularity build nipype-ants.sif Singularity

This will create a new file :code:`nipype-ants.sif` in this directory. This is the
Singularity container. You can move this file around like any other file -- even share
it with all of your friends.

To run Jupyter Notebook, use the following:

.. code-block::

    singularity run --bind $PWD:/work --pwd /work nipype-ants.sif jupyter-notebook

Feel free to create a new notebook and :code:`import nipype`.


Minify a Docker container
-------------------------

.. todo:: fill in instructions

*Neurodocker* enables you to minify Docker containers for a set of commands. This will
remove files not used by these commands and will dramatically reduce the size of the
Docker image.

See :code:`neurodocker minify --help` for more information.
