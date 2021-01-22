"""Minify a Docker container.

This program removes all files under specified directories in the container _not_ used
by the given command(s).
"""

import collections
import io
import logging
from pathlib import Path
import tarfile
import typing as ty

try:
    import docker
except ImportError:
    raise ImportError(
        "The `docker` Python package is required for minification functions."
    )

# Let these methods raise exceptions if they must.
client = docker.from_env()
if not client.ping():
    raise docker.errors.DockerException("Could not communicate with the Docker Engine")

logger = logging.getLogger(__name__)

_trace_script = Path(__file__).parent / "_trace.sh"
_prune_script = Path(__file__).parent / "_prune.py"

# Sync with _trace.sh
_log_prefix = "NEURODOCKER (in container):"


def copy_file_to_container(
    container: ty.Union[str, docker.models.containers.Container],
    src: ty.Union[str, Path],
    dest: ty.Union[str, Path],
) -> bool:
    """Copy `local_filepath` into `container`:`container_path`.

    Parameters
    ----------
    container : str or `docker.models.containers.Container` instance
        Container to which file is copied.
    src : str or `pathlib.Path` instance
        Filepath on the host.
    dest : str or `pathlib.Path` instance
        Directory inside container. Original filename is preserved.

    Returns
    -------
    success : bool
        True if copy was a success. False otherwise.
    """
    src = Path(src)
    dest = Path(dest)
    if not isinstance(container, docker.models.containers.Container):
        container = client.containers.get(container)
    # https://gist.github.com/zbyte64/6800eae10ce082bb78f0b7a2cca5cbc2
    with io.BytesIO() as tar_stream:
        with tarfile.TarFile(fileobj=tar_stream, mode="w") as tar:
            filename = src.name
            tar.add(src, arcname=filename, recursive=False)
        tar_stream.seek(0)
        return container.put_archive(str(dest), tar_stream)


def _get_mounts(container: docker.models.containers.Container) -> dict:
    # [
    #     {
    #         "Type": "bind",
    #         "Source": "/path/to/source",
    #         "Destination": "/destination",
    #         "Mode": "ro",
    #         "RW": False,
    #         "Propagation": "rprivate",
    #     }
    # ]
    return client.api.inspect_container(container)["Mounts"]


def trace_and_prune(
    container: ty.Union[str, docker.models.containers.Container],
    commands: ty.List[str],
    directories_to_prune: ty.Union[ty.List[str], ty.List[Path]],
) -> None:
    """Trace commands in the container, and remove all files in `directories_to_prune`
    that were not used by the commands.
    """
    # TODO: add examples to docstring.

    if not isinstance(container, docker.models.containers.Container):
        container = client.containers.get(container)
    if isinstance(commands, str):
        commands = [commands]
    if isinstance(directories_to_prune, (str, Path)):
        directories_to_prune = [directories_to_prune]

    directories_to_prune = [Path(p) for p in directories_to_prune]
    cmds = " ".join('"{}"'.format(c) for c in commands)

    # Copy the trace.sh file into the container and run it.
    copy_file_to_container(container, _trace_script, "/tmp/")
    trace_cmd = f"bash /tmp/_trace.sh {cmds}"
    logger.info(f"running command within container {container.id}: {trace_cmd}")

    # Run container. We need to use the lower-level docker-py API to have access to the
    # exec_id. Using the exec_id, we can test for the exec's exit code with each
    # iteration.
    exec_dict: dict = container.client.api.exec_create(container.id, cmd=trace_cmd)
    exec_id: str = exec_dict["Id"]
    log_gen: ty.Generator[bytes, None, None] = container.client.api.exec_start(
        exec_id, stream=True
    )

    # Hold N lines of context. If there is an error during container execution, this
    # context is shown to the user to give them a better idea of what went wrong.
    context: ty.Deque[str] = collections.deque([], maxlen=10)
    exit_code: int
    for log in log_gen:
        log_str = log.decode().strip()
        context.append(log_str)
        logger.info(log_str)
    exit_code = client.api.exec_inspect(exec_id)["ExitCode"]
    if exit_code != 0:
        # Print the lines of context in reverse order so last line is at the bottom.
        ctx_msg = "\n".join(list(context)[::-1])
        raise RuntimeError(f"error in container:\n{ctx_msg}")

    # Get files to prune.
    copy_file_to_container(container, _prune_script, "/tmp/")
    ret, result = container.exec_run(
        "/tmp/reprozip-miniconda/bin/python /tmp/_prune.py"
        " --config-file /tmp/neurodocker-reprozip-trace/config.yml"
        " --dirs-to-prune {}".format(" ".join(map(str, directories_to_prune))).split()
    )
    result = result.decode().strip()
    if ret != 0:
        raise RuntimeError(f"Failed: {result}")

    ret, result = container.exec_run(
        ["cat", "/tmp/neurodocker-reprozip-trace/TO_DELETE.list"]
    )
    result = result.decode().strip()
    if ret != 0:
        raise RuntimeError(f"Error: {result}")

    files_to_remove = [Path(p) for p in result.splitlines()]
    if not len(files_to_remove):
        print("No files to remove. Quitting.")
        return

    # Check if any files to be removed are in mounted directories.
    mounts = _get_mounts(container.id)
    if mounts:
        for m in mounts:
            for p in files_to_remove:
                if Path(m["Destination"]) in Path(p).parents:
                    raise ValueError(
                        "Attempting to remove files in a mounted directory.  Directory"
                        f" in the container '{m['Destination']}' is host directory"
                        f" '{m['Source']}'. Remove this mounted directory from the"
                        " minification command and rerun."
                    )

    print("\nWARNING!!! THE FOLLOWING FILES WILL BE REMOVED:")
    print("\n    ", end="")
    print("\n    ".join(sorted(map(str, files_to_remove))))
    print(
        "\nWARNING: PROCEEDING MAY RESULT IN IRREVERSIBLE DATA LOSS, FOR EXAMPLE"
        " IF ATTEMPTING TO REMOVE FILES IN DIRECTORIES MOUNTED FROM THE HOST."
        " PROCEED WITH EXTREME CAUTION! NEURODOCKER ASSUMES NO RESPONSIBILITY"
        " FOR DATA LOSS. ALL OF THE FILES LISTED ABOVE WILL BE REMOVED."
    )
    response = "placeholder"
    try:
        while response.lower() not in {"y", "n", ""}:
            response = input("Proceed (y/N)? ")
    except KeyboardInterrupt:
        print("\nQuitting.")
        return

    if response.lower() in {"", "n"}:
        print("Quitting.")
        return

    print("Removing files ...")
    ret, result = container.exec_run(
        'xargs -d "\n" -a /tmp/neurodocker-reprozip-trace/TO_DELETE.list rm -f'
    )
    result = result.decode().split()
    if ret:
        raise RuntimeError(f"Error: {result}")

    ret, result = container.exec_run(
        "rm -rf /tmp/neurodocker-reprozip-trace /tmp/reprozip-miniconda"
        " /tmp/_trace.sh /tmp/_prune.py"
    )
    result = result.decode().split()
    if ret:
        raise RuntimeError(f"Error: {result}")

    print("\n\nFinished removing files.")
    print("Next, create a new Docker image with the minified container:")
    print(f"\n    docker export {container.name} | docker import - imagename\n")


def main():
    from argparse import ArgumentParser

    p = ArgumentParser(description=__doc__)
    p.add_argument("-c", "--container", required=True, help="Running container.")
    p.add_argument(
        "-d",
        "--dirs-to-prune",
        required=True,
        nargs="+",
        help="Directories to prune. Data will be lost in these directories.",
    )
    p.add_argument("--commands", required=True, nargs="+", help="Commands to minify.")
    args = p.parse_args()

    trace_and_prune(
        container=args.container,
        commands=args.commands,
        directories_to_prune=args.dirs_to_prune,
    )
