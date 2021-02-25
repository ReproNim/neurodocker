"""Minify a Docker container.

This program removes all files under specified directories in the container _not_ used
by the given command(s).
"""

# TODO: consider implementing custom types for Docker container and paths within a
# Docker container.

import io
import logging
from pathlib import Path
import tarfile
import typing as ty

import click

try:
    import docker
except ImportError:
    raise ImportError(
        "The `docker` Python package is required for minification functions."
    )

try:
    client = docker.from_env()
    if not client.ping():
        raise RuntimeError("Could not communicate with the Docker Engine.")
except docker.errors.DockerException:
    raise RuntimeError("Could not create a Docker client.")

logger = logging.getLogger(__name__)

_trace_script = Path(__file__).parent / "_trace.sh"
_prune_script = Path(__file__).parent / "_prune.py"


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


@click.command()
@click.option(
    "-c", "--container", required=True, help="ID or name of running Docker container"
)
@click.option(
    "-d",
    "--dir",
    "directories_to_prune",
    required=True,
    multiple=True,
    help="Directories in container to prune. Data will be lost in these directories",
)
@click.option("--yes", is_flag=True, help="Reply yes to all prompts.")
@click.argument("command", nargs=-1, required=True)
def minify(
    container: ty.Union[str, docker.models.containers.Container],
    directories_to_prune: ty.Tuple[str],
    yes: bool,
    command: ty.Tuple[str],
) -> None:
    """Minify a container.

    Trace COMMAND... in the container, and remove all files in `--dirs-to-prune` that
    were not used by the commands.

    \b
    Examples
    --------
    docker run --rm -itd --name to-minify python:3.9-slim bash
    neurodocker minify \\
        --container to-minify \\
        --dir /usr/local \\
        "python -c 'a = 1 + 1; print(a)'"
    """
    container = client.containers.get(container)
    container = ty.cast(docker.models.containers.Container, container)

    cmds = " ".join(f'"{c}"' for c in command)

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
    for log in log_gen:
        log_str = log.decode().strip()
        click.secho(log_str, fg="yellow")
    exit_code: int = client.api.exec_inspect(exec_id)["ExitCode"]
    if exit_code != 0:
        raise RuntimeError("error in container")

    # Get files to prune.
    copy_file_to_container(container, _prune_script, "/tmp/")
    ret: int
    result: bytes
    ret, result = container.exec_run(
        "/tmp/reprozip-miniconda/bin/python /tmp/_prune.py"
        " --config-file /tmp/neurodocker-reprozip-trace/config.yml"
        " --dirs-to-prune {}".format(" ".join(map(str, directories_to_prune))).split()
    )
    if ret != 0:
        raise RuntimeError(f"Failed: {result.decode().strip()}")

    ret, result = container.exec_run(
        ["cat", "/tmp/neurodocker-reprozip-trace/TO_DELETE.list"]
    )
    if ret != 0:
        raise RuntimeError(f"Error: {result.decode().strip()}")

    files_to_remove = [Path(p) for p in result.decode().strip().splitlines()]
    if not len(files_to_remove):
        print("No files to remove. Quitting.")
        return

    # Check if any files to be removed are in mounted directories.
    mounts = _get_mounts(container.id)
    if mounts:
        for m in mounts:
            for p in files_to_remove:
                if Path(m["Destination"]) in Path(p).parents:
                    click.get_current_context().fail(
                        "Attempting to remove files in a mounted directory.  Directory"
                        f" in the container '{m['Destination']}' is host directory"
                        f" '{m['Source']}'. Remove this mounted directory from the"
                        " minification command and rerun."
                    )

    click.secho("\nWARNING!!! THE FOLLOWING FILES WILL BE REMOVED:", fg="yellow")
    click.echo()
    click.echo("    " + "\n    ".join(sorted(map(str, files_to_remove))))
    click.secho(
        "\nWARNING: PROCEEDING MAY RESULT IN IRREVERSIBLE DATA LOSS, FOR EXAMPLE"
        " IF ATTEMPTING TO REMOVE FILES IN DIRECTORIES MOUNTED FROM THE HOST."
        " PROCEED WITH EXTREME CAUTION! NEURODOCKER ASSUMES NO RESPONSIBILITY"
        " FOR DATA LOSS. ALL OF THE FILES LISTED ABOVE WILL BE REMOVED.",
        fg="yellow",
    )
    if yes:
        click.secho("Proceeding because --yes was provided", fg="green")
    else:
        click.confirm("Proceed?", abort=True)
    click.echo("Removing files ...")
    ret, result = container.exec_run(
        'xargs -d "\n" -a /tmp/neurodocker-reprozip-trace/TO_DELETE.list rm -f'
    )
    if ret:
        raise RuntimeError(f"Error: {result.decode().split()}")

    ret, result = container.exec_run(
        "rm -rf /tmp/neurodocker-reprozip-trace /tmp/reprozip-miniconda"
        " /tmp/_trace.sh /tmp/_prune.py"
    )
    if ret:
        raise RuntimeError(f"Error: {result.decode().split()}")

    click.secho("\n\nFinished removing files.", fg="green")
    click.echo("Next, create a new Docker image with the minified container:")
    click.echo(f"\n    docker export {container.name} | docker import - imagename\n")
