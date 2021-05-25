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

Neurodocker can also be installed in a :code:`conda` environment (using :code:`pip`).

.. code-block:: bash

    conda create -n neurodocker python pyyaml
    conda activate neurodocker
    python -m pip install neurodocker
    neurodocker --help
