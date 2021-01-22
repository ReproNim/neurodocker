import pytest

from neurodocker.reproenv.exceptions import RendererError
from neurodocker.reproenv.renderers import SingularityRenderer
from neurodocker.reproenv.template import Template


def test_singularity_renderer_add_template():
    s = SingularityRenderer("apt")

    d = {
        "name": "foobar",
        "binaries": {
            "urls": {"1.0.0": "foobar"},
            "env": {"foo": "bar"},
            "instructions": (
                "{{self.install_dependencies()}}\necho hello {{ self.myname }}"
            ),
            "arguments": {"required": ["myname"], "optional": {}},
            "dependencies": {
                "apt": ["curl", "wget"],
                "debs": [],
                "yum": ["python", "wget"],
            },
        },
    }

    with pytest.raises(
        RendererError, match="template must be an instance of 'Template' but got"
    ):
        s.add_template(d, method="binaries")

    # Invalid method
    with pytest.raises(
        RendererError, match="method must be 'binaries', 'source' but got 'fakemethod'"
    ):
        s.add_template(Template(d, binaries_kwds=dict(myname="f")), method="fakemethod")

    # Test apt.
    s = SingularityRenderer("apt")
    s.add_template(Template(d, binaries_kwds=dict(myname="Bjork")), method="binaries")
    assert (
        str(s)
        == """\


%environment
export foo="bar"

%post
apt-get update -qq
apt-get install -y -q --no-install-recommends \\
    curl \\
    wget
rm -rf /var/lib/apt/lists/*
echo hello Bjork"""
    )

    d = {
        "name": "baz",
        "binaries": {
            "urls": {"1.0.0": "foobar"},
            "env": {"foo": "bar"},
            "instructions": (
                "{{self.install_dependencies()}}\necho hello {{ self.myname }}"
            ),
            "arguments": {"required": [], "optional": {"myname": "foo"}},
            "dependencies": {"apt": ["curl wget"], "debs": [], "yum": ["python wget"]},
        },
    }

    s = SingularityRenderer("apt")
    s.add_template(Template(d), method="binaries")
    assert (
        str(s)
        == """\


%environment
export foo="bar"

%post
apt-get update -qq
apt-get install -y -q --no-install-recommends \\
    curl wget
rm -rf /var/lib/apt/lists/*
echo hello foo"""
    )


def test_singularity_render_from_instance_methods():
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/"""
    )

    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR\""""
    )

    # Label
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    s.label(ORG="BAZ")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR"

%labels
ORG BAZ"""
    )

    # Run
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    s.label(ORG="BAZ")
    s.run("echo foobar")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR"

%post
echo foobar

%labels
ORG BAZ"""
    )

    # User
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    s.label(ORG="BAZ")
    s.run("echo foobar")
    s.user("nonroot")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR"

%post
echo foobar

test "$(getent passwd nonroot)" \\
|| useradd --no-user-group --create-home --shell /bin/bash nonroot


su - nonroot

%labels
ORG BAZ"""
    )

    # nonroot user
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    s.label(ORG="BAZ")
    s.run("echo foobar")
    s.user("nonroot")
    s.workdir("/opt/foo")
    s.user("root")
    s.user("nonroot")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR"

%post
echo foobar

test "$(getent passwd nonroot)" \\
|| useradd --no-user-group --create-home --shell /bin/bash nonroot


su - nonroot

mkdir -p /opt/foo
cd /opt/foo

su - root

su - nonroot

%labels
ORG BAZ"""
    )

    # run bash
    s = SingularityRenderer("apt")
    s.from_("alpine")
    s.copy(["foo/bar/baz.txt", "foo/baz/cat.txt"], "/opt/")
    s.env(FOO="BAR")
    s.label(ORG="BAZ")
    s.run("echo foobar")
    s.user("nonroot")
    s.workdir("/opt/foo")
    s.user("root")
    s.user("nonroot")
    s.run_bash("source activate")
    assert (
        str(s)
        == """\
Bootstrap: docker
From: alpine

%files
foo/bar/baz.txt /opt/
foo/baz/cat.txt /opt/

%environment
export FOO="BAR"

%post
echo foobar

test "$(getent passwd nonroot)" \\
|| useradd --no-user-group --create-home --shell /bin/bash nonroot


su - nonroot

mkdir -p /opt/foo
cd /opt/foo

su - root

su - nonroot

bash -c 'source activate'

%labels
ORG BAZ"""
    )
