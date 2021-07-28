Known Issues
============

- Using the :code:`-t/--tty` option in :code:`docker run` produces non-printable
  characters in the generated Dockerfile or Singularity recipe
  (see `moby/moby#8513 <https://github.com/moby/moby/issues/8513#issuecomment-216191236>`_).

  - Solution: do not use the :code:`-t/--tty` flag, unless using the container interactively.

- Attempting to rebuild into an existing Singularity image may raise an error.

  - Solution: remove the existing image or build a new image file.

- The default apt :code:`--install` option :code:`--no-install-recommends`
  (that aims to minimize container size) can cause unexpected behavior.

  - Solution: use :code:`--install opts="--quiet" package1 package2`

- FreeSurfer cannot find my license file.

  - Solution: get a free license from
    `FreeSurfer's website <https://surfer.nmr.mgh.harvard.edu/registration.html>`_, and
    copy it into the container. To build the Docker image, please use the form

        .. code-block:: bash

            docker build .

    instead of

        .. code-block:: bash

            docker build - < Dockerfile

    because the latter form will not copy files into the image.
