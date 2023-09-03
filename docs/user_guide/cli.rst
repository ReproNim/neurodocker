Command-line Interface
======================

Neurodocker provides the command-line program :code:`neurodocker`.
This program has two subcommands: :code:`generate` and :code:`minify`.

neurodocker
-----------

.. literalinclude:: cli_help.txt

neurodocker generate
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: generate_cli_help.txt

The ``neurodocker generate`` command has two subcommands: `docker` and `singularity`.
Most of the arguments for these subcommands are identical, but please check the details below.

neurodocker generate docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: generate_docker_cli_help.txt

neurodocker generate singularity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: generate_singularity_cli_help.txt

neurodocker minify
~~~~~~~~~~~~~~~~~~

.. note::

    Minifying images requires additional dependencies installed with :code: `pip`. Please install neurodocker with

    .. code-block::

        pip install neurodocker[minify]

.. literalinclude:: minify_cli_help.txt
