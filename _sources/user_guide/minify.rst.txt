Minify Containers
=================

Neurodocker provides a utility to minify existing Docker containers for specific
commands. This feature relies heavily on `ReproZip <https://www.reprozip.org/>`_.

.. note::

    Neurodocker must be installed with :code:`pip` to minify containers.

    .. code-block::

        pip install neurodocker[minify]

    The Docker engine must also be installed and running. You can confirm that
    Docker is installed and running by executing

    .. code-block::

        docker images

    on the command-line. If Docker is not available, the :code:`neurodocker minify`
    command will not be available.

Minify image with ANTs
----------------------

In the following example, a Docker image is built with ANTs version 2.3.1 and a
functional scan. The image is minified for running :code:`antsMotionCorr`.
The original ANTs Docker image is 1.96 GB, and the minified image is 369 MB.
The only directory that is pruned is :code:`/opt`, which includes the ANTs
installation. This means that important directories like :code:`/usr` and
:code:`/bin` are untouched, and the container can still be used interactively.

.. code-block:: bash

    # Create a Docker image with ANTs, and download a functional scan.
    download_cmd="curl -fsSL -o /home/func.nii.gz http://psydata.ovgu.de/studyforrest/phase2/sub-01/ses-movie/func/sub-01_ses-movie_task-movie_run-1_bold.nii.gz"
    neurodocker generate docker \
        --pkg-manager yum \
        --base-image centos:7 \
        --ants version=2.3.1 \
        --run="$download_cmd" \
        | docker build -t ants:2.3.1 -

    # Run the container in the background.
    docker run --rm -itd --name ants-container ants:2.3.1

    # Find all of the files under `/opt` that are not used by the command(s),
    # and queue those files for deletion.
    cmd="antsMotionCorr -d 3 -a /home/func.nii.gz -o /home/func_avg.nii.gz"
    neurodocker minify \
        --container ants-container \
        --dir /opt \
        "$cmd"
    # Read through the list of files that will be deleted, and respond with
    # the keyboard. Then, create a new Docker image using the pruned container.
    docker export ants-container | docker import - ants:2.3.1-min-motioncorr

    # View a summary of the Docker images.
    docker images
    # REPOSITORY   TAG                    IMAGE ID       CREATED             SIZE
    # ants         2.3.1-min-motioncorr   597aedcbf7fc   2 minutes ago       369MB
    # ants         2.3.1                  4fda1f47feb2   4 minutes ago       1.96GB
    # centos       7                      8652b9f0cb4c   3 months ago        204MB
