from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.tests.utils import skip_if_no_docker


@skip_if_no_docker
def test_build_a(tmp_path):
    import docker

    client = docker.from_env()

    # Create a Dockerfile.
    d = DockerRenderer("apt")
    d.from_("debian:buster-slim", as_="builder")
    d.arg("FOO")
    d.copy(["foo.txt", "tst/baz.txt"], "/opt/")
    d.env(PATH="$PATH:/opt/foo/bin")
    d.label(ORG="myorg")
    d.run("echo foobar")
    d.user("nonroot")
    d.workdir("/opt/foobar")
    d.entrypoint(["printf", "hi there"])

    # Create the paths that are copied in the Dockerfile.
    (tmp_path / "tst").mkdir(exist_ok=True)
    with (tmp_path / "foo.txt").open("w"):
        pass
    with (tmp_path / "tst" / "baz.txt").open("w"):
        pass
    # Write Dockerfile.
    (tmp_path / "Dockerfile").write_text(str(d))
    image = client.images.build(path=str(tmp_path), tag="test", rm=True)
    # This is a tuple...
    image = image[0]
    stdout = client.containers.run(image=image, entrypoint="ls /opt")
    assert set(stdout.decode().splitlines()) == {"baz.txt", "foo.txt", "foobar"}

    stdout = client.containers.run(image=image)
    assert stdout.decode().strip() == "hi there"
