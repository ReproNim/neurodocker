import logging
from pathlib import Path

import pytest
import yaml

from neurodocker.reproenv.renderers import DockerRenderer, SingularityRenderer
from neurodocker.reproenv.template import Template


@pytest.mark.parametrize("renderer_cls", [DockerRenderer, SingularityRenderer])
@pytest.mark.parametrize(
    "image, name, version, missing",
    [
        ("debian:bullseye", "spm12", "r7771", "multiarch-support"),
        ("debian:11-slim", "matlabmcr", "2010a", "openjdk-8-jre"),
        ("docker.io/library/debian:bookworm-slim", "mrtrix3", "3.0.4", "libtiff5"),
        ("debian:12.9@sha256:abc", "mrtrix3", "3.0.4", "libtiff5"),
        ("debian:trixie", "matlabmcr", "2023b", "libncurses5"),
    ],
)
def test_warn_about_unavailable_dependencies(
    renderer_cls, image, name, version, missing, caplog
):
    path = Path(__file__).parents[2] / "templates" / f"{name}.yaml"
    template = Template(
        yaml.safe_load(path.read_text()), binaries_kwds={"version": version}
    )
    renderer = renderer_cls(pkg_manager="apt").from_(image)
    with caplog.at_level(logging.WARNING):
        renderer.add_template(template, method="binaries")
    assert name in caplog.text
    assert image in caplog.text
    assert missing in caplog.text
    assert "unavailable" in caplog.text
    assert "unavailable" not in str(renderer)


@pytest.mark.parametrize(
    "image", ["debian:bullseye", "private/debian:bookworm", "debian", "debian:latest"]
)
def test_no_false_compatibility_claims(image, caplog):
    renderer = DockerRenderer(pkg_manager="apt").from_(image)
    template = Template(
        {
            "name": "example",
            "url": "example.org",
            "source": {
                "dependencies": {"apt": ["libtiff5"]},
                "instructions": "{{ self.install_dependencies() }}",
            },
        }
    )
    renderer.add_template(template, method="source")
    assert not caplog.records


def test_checks_current_stage_and_package_manager(caplog):
    template = Template(
        {
            "name": "example",
            "url": "example.org",
            "source": {
                "dependencies": {"apt": ["libtiff5"]},
                "instructions": "echo ok",
            },
        }
    )
    renderer = DockerRenderer(pkg_manager="apt").from_("debian:bookworm")
    renderer.from_("debian:bullseye").add_template(template, method="source")
    DockerRenderer(pkg_manager="yum").from_("debian:bookworm").add_template(
        template, method="source"
    )
    assert not caplog.records


@pytest.mark.parametrize(
    "image",
    ["debian:bookworm", "library/debian:12", "index.docker.io/library/debian:12-slim"],
)
def test_versioned_and_architecture_qualified_packages(image):
    from neurodocker.reproenv.apt import unavailable_apt_packages

    assert unavailable_apt_packages(image, ["libtiff5:amd64=4.2", "dbus-x11"]) == [
        "libtiff5:amd64=4.2"
    ]
