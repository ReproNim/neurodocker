from pathlib import Path

from click.testing import CliRunner
import pytest

from neurodocker.cli.minify.trace import minify

docker = pytest.importorskip("docker", reason="docker-py not found")


@pytest.mark.skip(reason="ptrace no longer supported under docker")
def test_minify():
    client = docker.from_env()
    container = client.containers.run("python:3.9-slim", detach=True, tty=True,
                                      platform="Linux/amd64", privileged=True)
    commands = ["python --version", """python -c 'print(123)'"""]
    try:
        runner = CliRunner()
        result = runner.invoke(
            minify,
            ["--container", container.id, "--dir", "/usr/local"] + commands,
            input="y",
        )
        print(result.output)
        assert result.exit_code == 0

        # Test that the commands can still be run.
        for cmd in commands:
            ret, result = container.exec_run(cmd)
            result = result.decode()
            assert ret == 0, f"unexpected non-zero return code when running '{cmd}'"

        # This should fail.
        ret, result = container.exec_run("pip --help")
        assert ret != 0, f"unexpected zero return code when running '{cmd}'"

    finally:
        container.stop()
        container.remove()


@pytest.mark.skip(reason="ptrace no longer supported under docker")
def test_minify_abort():
    client = docker.from_env()
    container = client.containers.run("python:3.9-slim", detach=True, tty=True)
    commands = ["python --version", """python -c 'print(123)'"""]
    try:
        runner = CliRunner()
        result = runner.invoke(
            minify,
            ["--container", container.id, "--dir", "/usr/local"] + commands,
            input="n",  # abort
        )
        assert result.exit_code != 0

        # Test that the commands can still be run.
        for cmd in commands:
            ret, result = container.exec_run(cmd)
            result = result.decode()
            assert ret == 0, f"unexpected non-zero return code when running '{cmd}'"

        # This should still succeed.
        ret, result = container.exec_run("pip --help")
        assert ret == 0, f"unexpected non-zero return code when running '{cmd}'"

    finally:
        container.stop()
        container.remove()

@pytest.mark.skip(reason="ptrace no longer supported under docker")
def test_minify_with_mounted_volume(tmp_path: Path):
    client = docker.from_env()

    # Create a file in a mounted directory.
    (tmp_path / "foobar.txt").write_text("Foobar")

    container = client.containers.run(
        "python:3.8-slim",
        detach=True,
        tty=True,
        volumes={str(tmp_path): {"bind": "/work", "mode": "rw"}},
    )
    commands = ["python --version", "python -c 'print()'"]

    try:
        runner = CliRunner()
        result = runner.invoke(
            minify,
            ["--container", container.id, "--dir", "/usr/local", "--dir", "/work"]
            + commands,
        )
        assert result.exit_code != 0
        assert "Attempting to remove files in a mounted directory" in result.output

        runner = CliRunner()
        result = runner.invoke(
            minify,
            ["--container", container.id, "--dir", "/usr/local"] + commands,
            input="y",
        )
        assert result.exit_code == 0
    finally:
        container.stop()
        container.remove()
