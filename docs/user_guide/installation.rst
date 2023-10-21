Installation
============

container (preferred)
---------------------

We recommend using the Neurodocker Docker image, which can be access through
Docker or Singularity.

.. code-block:: bash

    docker run --rm repronim/neurodocker:latest --help

Note: Some tools require an interactive input during installation (e.g. FSL). This can either be handled using the Neurodocker `--yes` option (see examples -> FSL) or running the container interactively will also allow to answer this question:

.. code-block:: bash

    docker run -i --rm

Alternatively, a singularity container:

.. code-block:: bash

    singularity run docker://repronim/neurodocker:latest --help

Note: The version tag `latest` is a moving target and points to the latest stable release.

.. code-block:: bash

    repronim/neurodocker:latest -> latest release (0.9.4 now)
    repronim/neurodocker:master -> master branch
    repronim/neurodocker:0.9.4
    repronim/neurodocker:0.9.2
    repronim/neurodocker:0.9.1
    repronim/neurodocker:0.9.0
    repronim/neurodocker:0.8.0
    repronim/neurodocker:0.7.0
    ...

pip
---

Neurodocker can also be installed with :code:`pip`. This is useful if you want to use
the Neurodocker Python API. Python 3.7 or newer is required.

.. code-block:: bash

    python -m pip install neurodocker
    neurodocker --help

conda
-----

We recommend using a virtual environment or a :code:`conda` environment.
In order to create a new :code:`conda` environment and install Neurodocker:

.. code-block:: bash

    conda create -n neurodocker python=3.9
    conda activate neurodocker
    python -m pip install neurodocker
    neurodocker --help
