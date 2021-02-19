Command-line Interface
======================

Neurodocker provides the command-line program :code:`neurodocker`.
This program has two subcommands: :code:`generate` and :code:`minify`.

neurodocker
-----------

 .. code-block::

    Usage: neurodocker [OPTIONS] COMMAND [ARGS]...

    Generate custom containers, and minify existing containers.

    Options:
    --version  Show the version and exit.
    --help     Show this message and exit.

    Commands:
    generate  Generate a container.
    minify    Minify a container.

neurodocker generate
~~~~~~~~~~~~~~~~~~~~

.. code-block::

    Usage: neurodocker generate [OPTIONS] COMMAND [ARGS]...

    Generate a container.

    Options:
    --template-path DIRECTORY  Path to directories with templates to register
                                [env var: REPROENV_TEMPLATE_PATH]

    --help                     Show this message and exit.

    Commands:
    docker       Generate a Dockerfile.
    singularity  Generate a Singularity recipe.


neurodocker generate docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    Usage: neurodocker generate docker [OPTIONS]

    Generate a Dockerfile.

    Options:
    -p, --pkg-manager [apt|yum]  System package manager  [required]
    -b, --base-image TEXT        Base image  [required]
    --arg KEY=VALUE              Build-time variables (do not persist after
                                container is built)

    --copy TEXT                  Copy files into the container. Provide at least
                                two paths. The last path is always the
                                destination path in the container.

    --env KEY=VALUE              Set persistent environment variables
    --install TEXT               Install packages with system package manager
    --label KEY=VALUE            Set labels on the container
    --run TEXT                   Run commands in /bin/sh
    --run-bash TEXT              Run commands in a bash shell
    --user TEXT                  Switch to a different user (create user if it
                                does not exist)

    --workdir TEXT               Set the working directory
    --_header KEY=VALUE          Add _header
                                    method=[source]
                                    options for method=source

    --afni KEY=VALUE             Add afni
                                    method=[binaries|source]
                                    options for method=binaries
                                    - install_path [default: /opt/afni-{{ self.version }}]
                                    - version [default: latest]
                                    - install_r_pkgs [default: false]
                                    - install_python3 [default: false]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/afni-{{ self.version }}]
                                    - install_r_pkgs [default: false]
                                    - install_python3 [default: false]

    --ants KEY=VALUE             Add ants
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[2.3.4|2.3.2|2.3.1|2.3.0|2.2.0|2.1.0|2.0.3|2.0.0]
                                    - install_path [default: /opt/ants-{{ self.version }}]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/ants-{{ self.version }}]
                                    - cmake_opts [default: -DCMAKE_INSTALL_PREFIX={{ self.install_path }} -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF]
                                    - make_opts [default: -j1]

    --convert3d KEY=VALUE        Add convert3d
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[nightly|1.0.0]
                                    - install_path [default: /opt/convert3d-{{ self.version }}]

    --dcm2niix KEY=VALUE         Add dcm2niix
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[v1.0.20201102|v1.0.20200331|v1.0.20190902|latest]
                                    - install_path [default: /opt/dcm2niix-{{ self.version }}]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/dcm2niix-{{ self.version }}]
                                    - cmake_opts [default: ]
                                    - make_opts [default: -j1]

    --freesurfer KEY=VALUE       Add freesurfer
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[7.1.1-min|7.1.1|7.1.0|6.0.1|6.0.0-min|6.0.0]
                                    - install_path [default: /opt/freesurfer-{{ self.version }}]
                                    - exclude_paths [default: average/mult-comp-cor
                                lib/cuda
                                lib/qt
                                subjects/V1_average
                                subjects/bert
                                subjects/cvs_avg35
                                subjects/cvs_avg35_inMNI152
                                subjects/fsaverage3
                                subjects/fsaverage4
                                subjects/fsaverage5
                                subjects/fsaverage6
                                subjects/fsaverage_sym
                                trctrain
                                ]

    --fsl KEY=VALUE              Add fsl
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[6.0.4|6.0.3|6.0.2|6.0.1|6.0.0|5.0.9|5.0.8|5.0.11|5.0.10]
                                    - install_path [default: /opt/fsl-{{ self.version }}]
                                    - exclude_paths [default: ]
                                **Note**: FSL is non-free. If you are considering commercial use of FSL, please consult the relevant license(s).

    --jq KEY=VALUE               Add jq
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.6|1.5]
                                    options for method=source
                                    - version [required]

    --minc KEY=VALUE             Add minc
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.9.15]
                                    - install_path [default: /opt/minc-{{ self.version }}]

    --miniconda KEY=VALUE        Add miniconda
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[latest|*]
                                    - install_path [default: /opt/miniconda-{{ self.version }}]
                                    - installed [default: false]
                                    - env_name [default: base]
                                    - env_exists [default: true]
                                    - conda_install [default: ]
                                    - pip_install [default: ]
                                    - conda_opts [default: ]
                                    - pip_opts [default: ]
                                    - yaml_file [default: ]

    --mricron KEY=VALUE          Add mricron
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.0.20190902|1.0.20190410|1.0.20181114|1.0.20180614|1.0.20180404|1.0.20171220]
                                    - install_path [default: /opt/mricron-{{ self.version }}]

    --mrtrix3 KEY=VALUE          Add mrtrix3
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[3.0.2|3.0.1|3.0.0]
                                    - install_path [default: /opt/mrtrix3-{{ self.version }}]
                                    - build_processes [default: 1]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/mrtrix3-{{ self.version }}]
                                    - build_processes [default: ]

    --ndfreeze KEY=VALUE         Add ndfreeze
                                    method=[source]
                                    options for method=source
                                    - date [required]
                                    - opts [default: ]

    --neurodebian KEY=VALUE      Add neurodebian
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[usa-tn|usa-nh|usa-ca|japan|greece|germany-munich|germany-magdeburg|china-zhejiang|china-tsinghua|china-scitech|australia]
                                    - os_codename [required]
                                    - full_or_libre [default: full]

    --petpvc KEY=VALUE           Add petpvc
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.2.4|1.2.2|1.2.1|1.2.0-b|1.2.0-a|1.1.0|1.0.0]
                                    - install_path [default: /opt/petpvc-{{ self.version }}]

    --spm12 KEY=VALUE            Add spm12
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[r7771|r7487|r7219|r6914|r6685|r6472|r6225|dev]
                                    - install_path [default: /opt/spm12-{{ self.version }}]
                                    - matlab_install_path [default: /opt/matlab-compiler-runtime-2010a]

    --vnc KEY=VALUE              Add vnc
                                    method=[source]
                                    options for method=source
                                    - passwd [required]

    --help                       Show this message and exit.

neurodocker generate singularity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    Usage: neurodocker generate singularity [OPTIONS]

    Generate a Singularity recipe.

    Options:
    -p, --pkg-manager [apt|yum]  System package manager  [required]
    -b, --base-image TEXT        Base image  [required]
    --arg KEY=VALUE              Build-time variables (do not persist after
                                container is built)

    --copy TEXT                  Copy files into the container. Provide at least
                                two paths. The last path is always the
                                destination path in the container.

    --env KEY=VALUE              Set persistent environment variables
    --install TEXT               Install packages with system package manager
    --label KEY=VALUE            Set labels on the container
    --run TEXT                   Run commands in /bin/sh
    --run-bash TEXT              Run commands in a bash shell
    --user TEXT                  Switch to a different user (create user if it
                                does not exist)

    --workdir TEXT               Set the working directory
    --_header KEY=VALUE          Add _header
                                    method=[source]
                                    options for method=source

    --afni KEY=VALUE             Add afni
                                    method=[binaries|source]
                                    options for method=binaries
                                    - install_path [default: /opt/afni-{{ self.version }}]
                                    - version [default: latest]
                                    - install_r_pkgs [default: false]
                                    - install_python3 [default: false]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/afni-{{ self.version }}]
                                    - install_r_pkgs [default: false]
                                    - install_python3 [default: false]

    --ants KEY=VALUE             Add ants
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[2.3.4|2.3.2|2.3.1|2.3.0|2.2.0|2.1.0|2.0.3|2.0.0]
                                    - install_path [default: /opt/ants-{{ self.version }}]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/ants-{{ self.version }}]
                                    - cmake_opts [default: -DCMAKE_INSTALL_PREFIX={{ self.install_path }} -DBUILD_SHARED_LIBS=ON -DBUILD_TESTING=OFF]
                                    - make_opts [default: -j1]

    --convert3d KEY=VALUE        Add convert3d
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[nightly|1.0.0]
                                    - install_path [default: /opt/convert3d-{{ self.version }}]

    --dcm2niix KEY=VALUE         Add dcm2niix
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[v1.0.20201102|v1.0.20200331|v1.0.20190902|latest]
                                    - install_path [default: /opt/dcm2niix-{{ self.version }}]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/dcm2niix-{{ self.version }}]
                                    - cmake_opts [default: ]
                                    - make_opts [default: -j1]

    --freesurfer KEY=VALUE       Add freesurfer
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[7.1.1-min|7.1.1|7.1.0|6.0.1|6.0.0-min|6.0.0]
                                    - install_path [default: /opt/freesurfer-{{ self.version }}]
                                    - exclude_paths [default: average/mult-comp-cor
                                lib/cuda
                                lib/qt
                                subjects/V1_average
                                subjects/bert
                                subjects/cvs_avg35
                                subjects/cvs_avg35_inMNI152
                                subjects/fsaverage3
                                subjects/fsaverage4
                                subjects/fsaverage5
                                subjects/fsaverage6
                                subjects/fsaverage_sym
                                trctrain
                                ]

    --fsl KEY=VALUE              Add fsl
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[6.0.4|6.0.3|6.0.2|6.0.1|6.0.0|5.0.9|5.0.8|5.0.11|5.0.10]
                                    - install_path [default: /opt/fsl-{{ self.version }}]
                                    - exclude_paths [default: ]
                                **Note**: FSL is non-free. If you are considering commercial use of FSL, please consult the relevant license(s).

    --jq KEY=VALUE               Add jq
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.6|1.5]
                                    options for method=source
                                    - version [required]

    --minc KEY=VALUE             Add minc
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.9.15]
                                    - install_path [default: /opt/minc-{{ self.version }}]

    --miniconda KEY=VALUE        Add miniconda
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[latest|*]
                                    - install_path [default: /opt/miniconda-{{ self.version }}]
                                    - installed [default: false]
                                    - env_name [default: base]
                                    - env_exists [default: true]
                                    - conda_install [default: ]
                                    - pip_install [default: ]
                                    - conda_opts [default: ]
                                    - pip_opts [default: ]
                                    - yaml_file [default: ]

    --mricron KEY=VALUE          Add mricron
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.0.20190902|1.0.20190410|1.0.20181114|1.0.20180614|1.0.20180404|1.0.20171220]
                                    - install_path [default: /opt/mricron-{{ self.version }}]

    --mrtrix3 KEY=VALUE          Add mrtrix3
                                    method=[binaries|source]
                                    options for method=binaries
                                    - version [required]
                                        version=[3.0.2|3.0.1|3.0.0]
                                    - install_path [default: /opt/mrtrix3-{{ self.version }}]
                                    - build_processes [default: 1]
                                    options for method=source
                                    - version [required]
                                    - install_path [default: /opt/mrtrix3-{{ self.version }}]
                                    - build_processes [default: ]

    --ndfreeze KEY=VALUE         Add ndfreeze
                                    method=[source]
                                    options for method=source
                                    - date [required]
                                    - opts [default: ]

    --neurodebian KEY=VALUE      Add neurodebian
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[usa-tn|usa-nh|usa-ca|japan|greece|germany-munich|germany-magdeburg|china-zhejiang|china-tsinghua|china-scitech|australia]
                                    - os_codename [required]
                                    - full_or_libre [default: full]

    --petpvc KEY=VALUE           Add petpvc
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[1.2.4|1.2.2|1.2.1|1.2.0-b|1.2.0-a|1.1.0|1.0.0]
                                    - install_path [default: /opt/petpvc-{{ self.version }}]

    --spm12 KEY=VALUE            Add spm12
                                    method=[binaries]
                                    options for method=binaries
                                    - version [required]
                                        version=[r7771|r7487|r7219|r6914|r6685|r6472|r6225|dev]
                                    - install_path [default: /opt/spm12-{{ self.version }}]
                                    - matlab_install_path [default: /opt/matlab-compiler-runtime-2010a]

    --vnc KEY=VALUE              Add vnc
                                    method=[source]
                                    options for method=source
                                    - passwd [required]

    --help                       Show this message and exit.


neurodocker minify
~~~~~~~~~~~~~~~~~~

.. note::

    Minifying images requires additional dependencies. Please install neurodocker with

    .. code-block::

        pip install neurodocker[minify]


.. code-block::

    Usage: neurodocker minify [OPTIONS] COMMAND...

    Minify a container.

    Trace COMMAND... in the container, and remove all files in `--dirs-to-
    prune` that were not used by the commands.

    Examples
    --------
    docker run --rm -itd --name to-minify python:3.9-slim bash
    neurodocker minify \
        --container to-minify \
        --dir /usr/local \
        "python -c 'a = 1 + 1; print(a)'"

    Options:
    -c, --container TEXT  ID or name of running Docker container  [required]
    -d, --dir TEXT        Directories in container to prune. Data will be lost
                            in these directories  [required]

    --help                Show this message and exit.
