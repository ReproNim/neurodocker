Installation
============

container (preferred)
---------------------

We recommend using the Neurodocker Docker image, which can be access through
Docker or Singularity.

.. code-block:: bash

    docker run --rm repronim/neurodocker:0.7.0 --help

.. code-block:: bash

    singularity run docker://repronim/neurodocker:0.7.0 --help

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
