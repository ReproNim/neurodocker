import pytest

from neurodocker.reproenv.exceptions import RendererError
from neurodocker.reproenv.renderers import _Renderer
from neurodocker.reproenv.renderers import DockerRenderer
from neurodocker.reproenv.renderers import SingularityRenderer


def test_renderer():
    with pytest.raises(RendererError):
        _Renderer(pkg_manager="foo")

    _Renderer("apt")
    assert _Renderer("yum").users == {"root"}
    assert _Renderer("apt", users={"root", "foo"}).users == {"root", "foo"}


@pytest.mark.parametrize("renderer_cls", [DockerRenderer, SingularityRenderer])
def test_renderer_eq(renderer_cls):
    # r: _Renderer = renderer("apt").from_("my_base_image").run("echo foobar")
    r = renderer_cls("apt").from_("my_base_image").run("echo foobar")
    # print(r)
    assert r == r
    assert r != f"{r}\necho foobar"
    # empty lines do not affect equality
    assert r == f"{r}\n"
    # comments do not count
    assert r == f"{r}\n# a comment"
    # inline comments count
    assert r != f"{r}\necho foo # inline comment"

    r2: _Renderer = renderer_cls("apt").from_("my_base_image").run("echo foobar")
    assert r == r2
    assert r2 == r
    r2.run("echo invalidate this")
    assert r != r2
    assert r2 != r


def test_not_implemented_methods():
    r = _Renderer("yum")
    with pytest.raises(NotImplementedError):
        r.arg(key="a", value="b")
    with pytest.raises(NotImplementedError):
        r.copy("", "")
    with pytest.raises(NotImplementedError):
        r.env(foo="bar")
    with pytest.raises(NotImplementedError):
        r.from_("baseimage")
    with pytest.raises(NotImplementedError):
        r.label(foo="bar")
    with pytest.raises(NotImplementedError):
        r.run("foo")
    with pytest.raises(NotImplementedError):
        # This is implemented but calls `.run()`
        r.run_bash("foo")
    with pytest.raises(NotImplementedError):
        r.user("nonroot")
    with pytest.raises(NotImplementedError):
        r.workdir("/opt/")


# TODO: add many tests for `indent`.
