Common Uses
===========

Create locally and use remotely
-------------------------------

.. todo::

    Add content.

Working with Data
-----------------

.. todo::

    Add content.

Jupyter Notebook
----------------

This example demonstrates how to build and run an image with Jupyter Notebook.

.. note::

    When you exit a Docker image, any files you created in that image are lost. So if
    you create Jupyter Notebooks while in a Docker image, remember to save them to
    a mounted directory. Otherwise, the notebooks will be deleted (and unrecoverable)
    after you exit the Docker image.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:bullseye-slim \
        --miniconda \
            version=latest \
            conda_install="matplotlib notebook numpy pandas seaborn" \
        --user nonroot \
        --workdir /work \
    > notebook.Dockerfile

    # Build the image.
    docker build --tag notebook --file notebook.Dockerfile .

    # Run the image. The current directory is mounted to the working directory of the
    # Docker image, so our notebooks are saved to the current directory.
    docker run --rm -it \
        --publish 8888:8888 \
        --volume $(pwd):/work notebook \
        jupyter-notebook --no-browser --ip 0.0.0.0


Multiple Conda Environments
---------------------------

This example demonstrates how to create a Docker image with multiple conda environments.

.. literalinclude:: common_uses/conda_multiple_env.txt

One can use the image in the following way:

.. code-block:: bash

    docker run --rm -it multi-conda-env bash
    # Pandas is installed in envA.
    conda activate envA
    python -c "import pandas"
    # Scipy is installed in envB.
    conda activate envB
    python -c "import scipy"
