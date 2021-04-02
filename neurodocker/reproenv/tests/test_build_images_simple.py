import pytest
import typing as ty

from neurodocker.reproenv.renderers import _Renderer
from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.renderers import SingularityRenderer
from neurodocker.reproenv.tests.utils import (
    build_docker_image,
    build_singularity_image,
    run_singularity_image,
)
from neurodocker.reproenv.tests.utils import run_docker_image
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

    rcls: ty.Type[_Renderer]

    if cmd == "docker":
        rcls = DockerRenderer
    else:
        rcls = SingularityRenderer

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

    if cmd == "docker":
        build_fn = build_docker_image
        run_fn = run_docker_image
    else:
        build_fn = build_singularity_image
        run_fn = run_singularity_image

    with build_fn(tmp_path) as img:
        stdout, _ = run_fn(img)
        assert stdout == "hi there"
        stdout, _ = run_fn(img, entrypoint=["ls"], args=["/opt/"])
        assert set(stdout.splitlines()) == {"baz.txt", "foo.txt", "foobar"}
