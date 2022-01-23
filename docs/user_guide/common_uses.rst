Common Uses
===========

Create locally and use remotely
-------------------------------

.. todo::

    Add content.

Working with Data
-----------------

These are some examples of common use-cases for different stages of the analysis life
cycle. Each example:

* Generates a ``Dockerfile`` with *Neurodocker* (using *Neurodocker* Docker image and ``debian:stretch`` base image) that includes specific versions of FSL and ANTs
* Builds the Docker image
* Runs a short processing script (both Bash and Python examples included here). For these examples, we simply skull strip a T1-weighted image with BET and warp it into MNI space with ANTs.

.. note::

    * These example Docker images include FSL and ANTs in order to provide somewhat realistic examples. However, downloading FSL can take some time and the images will be quite large (~12GB).
    * The commands in the example scripts likely will not produce good results and should not be used in any real analysis.

Running examples
****************

To run these examples, you will need Docker installed as we will use the *Neurodocker* docker image. The *Neurodocker* commands are explained in more detail at the end of this section.

To start, clone *Neurodocker* from Github and change directory to the cloned ``./neurodocker/docs/user_guide/working_with_data_example`` directory and create a directory for the output:

.. code-block:: bash

    cd ./neurodocker/docs/user_guide/working_with_data_example
    mkdir output

All the following commands assume they're being run from the ``./neurodocker/docs/user_guide/working_with_data_example`` directory.

Example 1
*********

This example creates an image that contains some neuroimaging software and uses a custom Bash script to process the data, reading the script and the data from the local file system, and writing data back to the local file system.

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries > Dockerfile

    # Build
    docker build -t neurodocker-example:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}:/home \
        -v ${PWD}/input:/home/input \
        -v ${PWD}/output:/home/output \
        neurodocker-example:main \
        bash /home/processing_script.sh

Example 2
*********

As for example 1, however here we run a processing script written in Python that also requires some additional Python packages. For this example, we're installing ``numpy`` ``pandas`` and ``nibabel`` with ``conda``. These packages are imported in the script for the sake of example, even though they aren't used.

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \
        --miniconda \
            conda_install="python=3.6 pandas numpy nibabel" \
            create_env="analysis" \
            activate=true > Dockerfile
    
    # Build
    docker build -t neurodocker-example-py:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}:/home \
        -v ${PWD}/input:/home/input \
        -v ${PWD}/output:/home/output \
        neurodocker-example-py:main \
        python3 /home/processing_script.py

Example 3
*********

Here we will add the processing scripts to the Docker image and automatically run the processing script on data that is accessed from the local file system. This would allow someone to process data from their local file system with the processing script included in the Docker image.

**Bash:**

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \
        --copy "processing_script.sh" "/home" \
        --add-to-entrypoint "bash /home/processing_script.sh" \
        --cmd "exit" > Dockerfile

    # Build
    docker build -t neurodocker-example:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}/input:/home/input \
        -v ${PWD}/output:/home/output \
        neurodocker-example:main


**Python:**

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \
        --miniconda \
            conda_install="python=3.6 pandas numpy nibabel" \
            create_env="analysis" \
            activate=true \
        --copy "processing_script.py" "/home" \
        --add-to-entrypoint "python3 /home/processing_script.py" \
        --cmd "exit" > Dockerfile
    
    # Build
    docker build -t neurodocker-example-py:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}/input:/home/input \
        -v ${PWD}/output:/home/output \
        neurodocker-example-py:main

Example 4
*********

As for example 3, however here the processing script and the data are added to the Docker image. This would allow someone to simply `run` the Docker image to execute the processing script on the data that is included in the Docker image, still writing the output to the local file system to be inspected. This approach may be useful for someone who doesn't need to see the processing scripts or data and simply wants to run the pipeline, get a result, and check it against a published paper.

Note that although the processing scripts and input data are included in the Docker image, we still need to ensure that the output directory exists on our local file system and it needs to be mounted to the output directory of the Docker container (`-v ${PWD}/output:/home/output`).

**Bash:**

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \
        --copy . "/home" \
        --run "mkdir -p /home/output" \
        --add-to-entrypoint "bash /home/processing_script.sh" \
        --cmd "exit" > Dockerfile

    # Build
    docker build -t neurodocker-example:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}/output:/home/output \
        neurodocker-example:main


**Python:**

.. code-block:: bash

    # Generate Dockerfile
    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \
        --miniconda \
            conda_install="python=3.6 pandas numpy nibabel" \
            create_env="analysis" \
            activate=true \
        --copy . "/home" \
        --run "mkdir -p /home/output" \
        --add-to-entrypoint "python3 /home/processing_script.py" \
        --cmd "exit" > Dockerfile
    
    # Build
    docker build -t neurodocker-example-py:main .

    # Run processing script
    docker run -it --rm \
        -v ${PWD}/output:/home/output \
        neurodocker-example-py:main

Components of *Neurodocker* command
***********************************

This component is common to all commands in these examples and simply selects the base image and the neuroimaging software to be included.

.. code-block:: bash

    docker run --rm repronim/neurodocker:master generate docker \
        --base=debian:stretch \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.2.0 method=binaries \

The Miniconda distribution is used for Docker images where Python is also required. In these examples we install Python version 3.6 and also use the `conda` package manager to install the additional packages. We then create a virtual environment within the Docker container and activate it automatically.

.. code-block:: bash

        --miniconda \
            conda_install="python=3.6 pandas numpy nibabel" \
            create_env="analysis" \
            activate=true \

Next we copy the processing script (example 3) or the script and the data (example 4) to the Docker image.

.. code-block:: bash

        # Copy script only
        --copy "processing_script.py" "/home" \

        # Copy everything in current working directory (here, scripts and data)
        --copy . "/home" \

Make sure the output directory exists in the Docker image.

.. code-block:: bash

        --run "mkdir -p /home/output" \

Set the processing script to be run automatically when the Docker container is initiated and return to the local command line when finished. The container entrypoint are commands that are run automatically when the container is initiated. Therefore, we're adding a command to run the processing script to be executed when the container is initiated. The last `> Dockerfile` component writes the output of the _Neurodocker_ command to a file called `Dockerfile`.

.. code-block:: bash

        --add-to-entrypoint "python3 /home/processing_script.py" \
        --cmd "exit" > Dockerfile

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
        --base-image debian:buster-slim \
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
    docker run --rm -it --publish 8888:8888 --volume $(pwd):/work notebook \
        jupyter-notebook --no-browser --ip 0.0.0.0


Multiple Conda Environments
---------------------------

This example demonstrates how to create a Docker image with multiple conda environments.

.. code-block:: bash

    neurodocker generate docker \
        --pkg-manager apt \
        --base-image debian:buster-slim \
        --miniconda \
            version=latest \
            env_name=envA \
            env_exists=false \
            conda_install=pandas \
        --miniconda \
            version=latest \
            installed=true \
            env_name=envB \
            env_exists=false \
            conda_install=scipy \
    > multi-conda-env.Dockerfile

    docker build --tag multi-conda-env --file multi-conda-env.Dockerfile .

One can use the image in the following way:

.. code-block:: bash

    docker run --rm -it multi-conda-env bash
    # Pandas is installed in envA.
    conda activate envA
    python -c "import pandas"
    # Scipy is installed in envB.
    conda activate envB
    python -c "import scipy"
