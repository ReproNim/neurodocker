import pytest

from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.renderers import SingularityRenderer
from neurodocker.reproenv.tests.utils import get_build_and_run_fns
from neurodocker.reproenv.tests.utils import skip_if_no_docker
from neurodocker.reproenv.tests.utils import skip_if_no_singularity


@pytest.mark.parametrize(
    "cmd",
    [
        pytest.param("docker", marks=skip_if_no_docker),
        pytest.param("singularity", marks=skip_if_no_singularity),
    ],
)
def test_build_simple(cmd: str, tmp_path):

    rcls = DockerRenderer if cmd == "docker" else SingularityRenderer

    # Create a Dockerfile.
    r = rcls("apt")
    if isinstance(r, DockerRenderer):
        r.from_("debian:buster-slim", as_="builder")
    else:
        r.from_("debian:buster-slim")
    r.arg("FOO")
    r.copy(["foo.txt", "tst/baz.txt"], "/opt/")
    r.env(PATH="$PATH:/opt/foo/bin")
    r.label(ORG="myorg")
    r.run("echo foobar")
    r.user("nonroot")
    r.workdir("/opt/foobar")
    r.entrypoint(["echo", "hi there"])

    # Create the paths that are copied in the Dockerfile.
    (tmp_path / "tst").mkdir(exist_ok=True)
    (tmp_path / "foo.txt").write_text("")
    (tmp_path / "tst" / "baz.txt").write_text("")

    spec = "Dockerfile" if cmd == "docker" else "Singularity"
    (tmp_path / spec).write_text(str(r))

    build_fn, run_fn = get_build_and_run_fns(cmd)
    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img)
        assert stdout == "hi there"
        stdout, _ = run_fn(img, entrypoint=["ls"], args=["/opt/"])
        assert set(stdout.splitlines()) == {"baz.txt", "foo.txt", "foobar"}
