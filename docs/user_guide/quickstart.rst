Quickstart
==========

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

**This requires having `Docker <https://docs.docker.com/get-docker/>`_ installed first**

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image neurodebian:bullseye \
        --ants version=2.4.3 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot

You should see a block of text appear in the console. This is the Dockerfile generated
by *Neurodocker*. Instructions in the Dockerfile are ordered in the same way as the
arguments in the command-line. To build a Docker image with this, save the output to a
file in an empty directory, and build with :code:`docker build`:

.. code-block:: bash

    # creating a new empty directory
    mkdir docker-example
    cd docker-example
    # saving the output of neurodocker command in a file: Dockerfile
    neurodocker generate docker \
        --pkg-manager apt \
        --base-image neurodebian:bullseye \
        --ants version=2.4.3 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot > Dockerfile
    # building a new image using the Dockerfile (use --file <dockerfile_name> option if other name is used)
    docker build --tag nipype-ants .

The image :code: `nipype-ants` contains :code: `ANTs` and a Python environment with :code: `Nipype` and :code: `Jupyter Notebook`.
You can start a Jupyter Notebook with the following command. This will mount
the current working directory to :code:`work` within the container, so any files you
create in this directory are saved. If we had not mounted this directory, all of the files
created in :code:`/work` would be gone after the container was stopped.
:code: `--publish 8888:8888` and :code: `--ip 0.0.0.0 --port 8888` is required in order to use Jupyter Notebook from a Docker container.

.. code-block:: bash

    docker run --rm -it \
        --workdir /work \
        --volume $PWD:/work \
        --publish 8888:8888 \
        nipype-ants jupyter-notebook --ip 0.0.0.0 --port 8888

Feel free to create a new notebook and :code:`import nipype`.

Singularity
~~~~~~~~~~~

In most cases the only difference between generating Dockerfile and
`Singularity definition file <https://sylabs.io/guides/3.7/user-guide/definition_files.html>`_ (the file that is used to create a Singularity container) is in
a form of :code:`neurodocker generate` command,  `neurodocker generate singularity` has to be used instead of :code:`neurodocker generate docker`.

**This requires having `Singularity <https://sylabs.io/guides/3.7/user-guide/quick_start.html>`_ installed first.**

.. code-block:: bash

    neurodocker generate singularity \
        --pkg-manager apt \
        --base-image neurodebian:bullseye\
        --ants version=2.4.3 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot

You should see a block of text appear in the console. This is the Singularity definition.
To build the Singularity image, create a new directory, save this output to a file, and
use :code:`sudo singularity build`. Note that this requires superuser privileges. You
will not be able to run this on a shared computing environment, like a high performance cluster.

.. code-block:: bash

    # creating a new empty directory
    mkdir singularity-example
    cd singularity-example
    # saving the output of the Neurodocker command in the Singularity file
    neurodocker generate singularity \
        --pkg-manager apt \
        --base-image neurodebian:bullseye\
        --ants version=2.4.3 \
        --miniconda version=latest conda_install="nipype notebook" \
        --user nonroot > Singularity
    # building a new image using the Singularity file
    sudo singularity build nipype-ants.sif Singularity

This will create a new file :code:`nipype-ants.sif` in this directory. This is the
Singularity container. You can move this file around like any other file -- even share
it with all of your friends.

To run Jupyter Notebook, use the following:

.. code-block:: bash

    singularity run --bind $PWD:/work --pwd /work nipype-ants.sif jupyter-notebook

Feel free to create a new notebook and :code:`import nipype`.


Minify a Docker container
-------------------------

*Neurodocker* enables you to minify Docker containers for a set of commands. This will
remove files not used by these commands and will dramatically reduce the size of the
Docker image.

See :code:`neurodocker minify --help` for more information.

.. note::

    Neurodocker must be installed with :code:`pip` to minify containers.

    .. code-block::

        pip install neurodocker[minify]

In the example below, we minify one of the official Python Docker images for certain
commands. This will remove all of the files in :code:`/usr/local/` that are not used by
these commands.

`ReproZip <https://www.reprozip.org/>`_ is used to determine the files used by the
commands.

.. code-block:: bash

    # running a container in the background and assigning `to-minify` name to the container
    docker run --rm -itd --name to-minify python:3.9-slim bash
    # running minify command for a specific set of python commands
    neurodocker minify \
      --container to-minify \
      --dir /usr/local \
      "python -c 'a = 1 + 1; print(a)'" \
      "python -c 'import os'"

You will be given a list of all of the files that will be deleted. Review this list of
files before proceeding.

.. code-block:: bash

    docker export to-minify | docker import - minified-python

Now if you run :code:`docker images`, the image :code:`minified-python` will be listed.

.. warning::

    Environment variables are lost when saving the minified image as a new image. If
    certain environment variables are required in the minified image, users should
    create a new Dockerfile that uses the minified image as a base image and then sets
    environment variables.

The commands that were run during minification will (read: should) succeed:

.. code-block:: bash

    docker run --rm minified-python python -c "a = 1 + 1; print(a)"
    docker run --rm minified-python python -c "import os"

But commands not run during minification are *not guaranteed to succeed*. The following
commands, for example, result in errors.

.. code-block:: bash

    docker run --rm minified-python python -c 'import math'
    docker run --rm minified-python python -c 'import pathlib'
    docker run --rm minified-python pip --help
