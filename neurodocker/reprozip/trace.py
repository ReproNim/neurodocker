"""Minimize existing Docker container with ReproZip.

Project repository: https://github.com/ViDA-NYU/reprozip/

See https://github.com/freesurfer/freesurfer/issues/70 for an example of using
ReproZip to minimize Freesurfer's recon-all command.


Current implementation
----------------------
A bash script (utils/reprozip_trace_runner.sh) implements items 1-3 below.

1. Install a dedicated Miniconda with ReproZip (not added to $PATH).
2. Run `reprozip trace ...` on an arbitrary number of commands.
3. Pack the experiment (`reprozip pack ...`)
4. Copy the pack file onto the host (done with `docker-py`).
    - at this point, the user is free to do anything with the pack file.
    - QUESTION: should this implementation do anything with this pack file
                after it is copied onto the host? eg, `reprounzip-docker setup`

Potential implementations
-------------------------
See https://github.com/kaczmarj/neurodocker/issues/23#issuecomment-307863219.

Notes
-----
1. To use the reprozip trace within a Docker container, the image/container
   must be built/run with `--security-opt seccomp:unconfined`.
      A. `docker build` does not allow --security-opt seccomp:unconfined on
          macOS.
2. Docker's use of layers means that even if a smaller container is committed
   from a larger image there will be no reduction in size (the previous layers
   are preserved). There is a `--squash` option in `docker build` that will
   merge all layers at the end of the build and remove files that were deleted
   in previous layers.
      A. The `--squash` option is experimental and might be changed or removed
         in the future.
      B. See https://github.com/moby/moby/issues/332
      C. See https://github.com/moby/moby/pull/22641
"""

import logging
import os

from neurodocker.utils import get_docker_client

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


def copy_file_to_container(container, src, dest):
    """Copy `local_filepath` into `container`:`container_path`.

    Parameters
    ----------
    container : str or container object
        Container to which file is copied.
    src : str
        Filepath on the host.
    dest : str
        Directory inside container. Original filename is preserved.

    Returns
    -------
    success : bool
        True if copy was a success. False otherwise.
    """
    # https://gist.github.com/zbyte64/6800eae10ce082bb78f0b7a2cca5cbc2

    from io import BytesIO
    import tarfile

    client = get_docker_client()

    try:
        container.put_archive
        container = container
    except AttributeError:
        container = client.containers.get(container)

    with BytesIO() as tar_stream:
        with tarfile.TarFile(fileobj=tar_stream, mode='w') as tar:
            filename = os.path.split(src)[-1]
            tar.add(src, arcname=filename, recursive=False)
        tar_stream.seek(0)
        return container.put_archive(dest, tar_stream)


def copy_file_from_container(container, src, dest='.'):
    """Copy file `filepath` from a running Docker `container`, and save it on
    the host to `save_path` with the original filename.

    Parameters
    ----------
    container : str or container object
        Container from which file is copied.
    src : str
        Filepath within container.
    dest : str
        Directory on the host in which to save file.

    Returns
    -------
    local_filepath : str
        Relative path to saved file on the host.
    """
    import tarfile
    import tempfile

    client = get_docker_client()

    try:
        container.put_archive
        container = container
    except AttributeError:
        container = client.containers.get(container)

    tar_stream, tar_info = container.get_archive(src)
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            for data in tar_stream:
                tmp.write(data)
            tmp.flush()
            with tarfile.TarFile(tmp.name) as tar:
                tar.extractall(path=dest)
        return os.path.join(dest, tar_info['name'])
    except Exception as e:
        raise
    finally:
        tar_stream.close()


class ReproZipMinimizer(object):
    """Minimize a container based on arbitrary number of commands. Can only be
    used at runtime (not while building a Docker image).

    Parameters
    ----------
    container : str or container object
        The container in which to trace commands.
    commands : str or list or tuple
        If str, one command to trace. If list or tuple, sequence of commands
        to trace in order.
    packfile_save_dir : str
        Directory on the host to save ReproZip pack file. Saves to current
        directory by default.
    """

    def __init__(self, container, commands, packfile_save_dir='.', **kwargs):

        try:
            container.put_archive
            self.container = container
        except AttributeError:
            client = get_docker_client()
            self.container = client.containers.get(container)

        if isinstance(commands, str):
            commands = [commands]
        self.commands = commands
        self.packfile_save_dir = packfile_save_dir

        self.shell_filepath = os.path.join(BASE_PATH, 'utils',
                                           'reprozip_trace_runner.sh')

    def run(self):
        """Install ReproZip, run `reprozip trace`, and copy pack file to host.

        Returns
        -------
        pack_filepath : str
            Absolute path to the saved pack file on the host.

        Raises
        ------
        RuntimeError : error occurs while running trace script in container.
        """
        import docker

        copy_file_to_container(self.container, self.shell_filepath, '/tmp/')

        cmds = ' '.join('"{}"'.format(c) for c in self.commands)

        trace_cmd = "bash /tmp/reprozip_trace_runner.sh " + cmds
        logger.debug("running command within container {}: {}"
                     "".format(self.container.id, trace_cmd))

        _, log_gen = self.container.exec_run(trace_cmd, stream=True)
        for log in log_gen:
            log = log.decode().strip()
            logger.debug(log)
            if (("REPROZIP" in log and "couldn't use ptrace" in log)
                    or "neurodocker (in container): error" in log.lower()
                    or "_pytracer.Error" in log):
                raise RuntimeError("Error: {}".format(log))

        self.pack_filepath = log.split()[-1].strip()
        print(log)
        print(self.pack_filepath)
        try:
            rel_pack_filepath = copy_file_from_container(
                self.container, self.pack_filepath, self.packfile_save_dir)
        except docker.errors.NotFound:
            raise RuntimeError(
                "ReproZip pack file was not found in the container. `reprozip"
                " trace` might have failed.")

        return os.path.abspath(rel_pack_filepath)
