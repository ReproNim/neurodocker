# TODO: add tests of individual CLI params.

from pathlib import Path

import pytest
from click.testing import CliRunner

from neurodocker.cli.cli import generate
from neurodocker.cli.generate import OptionEatAll

_cmds = ["docker", "singularity"]


@pytest.mark.parametrize("cmd", _cmds)
def test_fail_on_empty_args(cmd: str):
    runner = CliRunner()
    result = runner.invoke(generate, [cmd])
    assert result.exit_code != 0, result.output


@pytest.mark.parametrize("cmd", _cmds)
@pytest.mark.parametrize("pkg_manager", ["apt", "yum"])
def test_fail_on_no_base(cmd: str, pkg_manager: str):
    runner = CliRunner()
    result = runner.invoke(generate, [cmd, "--pkg-manager", pkg_manager])
    assert result.exit_code != 0, result.output


@pytest.mark.parametrize("cmd", _cmds)
def test_fail_on_no_pkg_manager(cmd: str):
    runner = CliRunner()
    result = runner.invoke(generate, [cmd, "--base-image", "debian"])
    assert result.exit_code != 0, result.output


@pytest.mark.parametrize("cmd", _cmds)
@pytest.mark.parametrize("pkg_manager", ["apt", "yum"])
def test_minimal_args(cmd: str, pkg_manager: str):
    runner = CliRunner()
    result = runner.invoke(
        generate, [cmd, "--pkg-manager", pkg_manager, "--base-image", "debian"]
    )
    assert result.exit_code == 0, result.output


def test_copy_issue_498():
    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            "docker",
            "--pkg-manager",
            "apt",
            "--base-image",
            "debian",
            # copy
            "--copy",
            "file1",
            "file2",
        ],
    )
    assert "file1" in result.output
    assert '\nCOPY ["file1", \\\n      "file2"]\n' in result.output

    # Fail if given fewer than two inputs to --copy.
    result = runner.invoke(
        generate,
        [
            "docker",
            "--pkg-manager",
            "apt",
            "--base-image",
            "debian",
            # copy
            "--copy",
            "file1",
        ],
    )
    assert "Error: expected at least two values for --copy" in result.output
    assert result.exit_code != 0


# Issue #498 references --copy but the same broken behavior is seen in --entrypoint.
def test_entrypoint_issue_498():
    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            "docker",
            "--pkg-manager",
            "apt",
            "--base-image",
            "debian",
            "--entrypoint",
            "printf",
            "this",
            "that",
        ],
    )
    assert '\nENTRYPOINT ["printf", "this", "that"]\n' in result.output


def test_optioneatall_type_issue_498():
    with pytest.raises(ValueError):
        OptionEatAll(["--foo"], type=str)
    OptionEatAll(["--foo"], type=tuple)


@pytest.mark.parametrize("cmd", _cmds)
@pytest.mark.parametrize("pkg_manager", ["apt", "yum"])
def test_all_args(cmd: str, pkg_manager: str):
    runner = CliRunner()
    result = runner.invoke(
        generate,
        [
            cmd,
            "--pkg-manager",
            pkg_manager,
            "--base-image",
            "debian",
            # arg
            "--arg",
            "ARG=VAL",
            # copy
            "--copy",
            "file1",
            "file2",
            "file3",
            # env
            "--env",
            "VAR1=CAT",
            "VAR2=DOG",
            # install
            "--install",
            "python3",
            "curl",
            # run
            "--run",
            "echo foobar",
            # run bash
            "--run-bash",
            "source activate",
            # user
            "--user",
            "nonroot",
            # workdir
            "--workdir",
            "/data",
        ],
    )
    assert result.exit_code == 0, result.output


# Test that a template can be rendered
# We need to use `reproenv generate` as the entrypoint here because the generate command
# is what registers the templates. Using the `docker` function
# (`reproenv generate docker`) directly does not fire `generate`.
@pytest.mark.parametrize("cmd", _cmds)
@pytest.mark.parametrize("pkg_manager", ["apt", "yum"])
def test_render_registered(cmd: str, pkg_manager: str):
    template_path = Path(__file__).parent
    runner = CliRunner(env={"REPROENV_TEMPLATE_PATH": str(template_path)})
    result = runner.invoke(
        generate,
        [
            cmd,
            "--base-image",
            "debian:buster",
            "--pkg-manager",
            pkg_manager,
            "--jq",
            "version=1.5",
            "--jq",
            "version=1.6",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "jq-1.5/jq-linux64" in result.output
    assert "jq-1.6/jq-linux64" in result.output
