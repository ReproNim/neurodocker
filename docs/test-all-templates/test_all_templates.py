"""Test all of the templates in neurodocker.

This can take **hours** to complete.
"""

import contextlib
from pathlib import Path
import subprocess
import typing as ty
import uuid

import pytest

from neurodocker.reproenv import DockerRenderer
from neurodocker.reproenv import SingularityRenderer
from neurodocker.reproenv import Template
from neurodocker.reproenv.state import registered_templates_items


def name_kwds_to_id(name: str, kwds: dict) -> str:
    ret = "-".join(f"{k}={v}" for (k, v) in kwds.items())
    return f"{name}-{ret}"


# TODO: use these context managers in neurodocker/reproenv tests.


@contextlib.contextmanager
def build_docker_image(context: Path):
    """Context manager that removes the built image on exit."""
    assert (context / "Dockerfile").exists()
    tag = uuid.uuid4().hex
    cmd: ty.List[str] = ["docker", "build", "--tag", tag, str(context)]
    try:
        _ = subprocess.check_output(cmd)
        yield tag
    finally:
        # do not force this, because perhaps others depend on the image
        subprocess.run(["docker", "image", "rm", tag])
        subprocess.run(["docker", "builder", "prune", "--force"])


@contextlib.contextmanager
def build_singularity_image(context: Path):
    """Context manager that removes the built image on exit."""
    recipe = context / "Singularity"
    assert recipe.exists()
    sif = context / f"{uuid.uuid4().hex}.sif"
    cmd: ty.List[str] = ["sudo", "singularity", "build", str(sif), str(recipe)]
    try:
        _ = subprocess.check_output(cmd)
        yield sif
    finally:
        sif.unlink(missing_ok=True)


def get_template_params() -> list:
    params = []
    for name, tmpl in registered_templates_items():
        template = Template(tmpl)
        if template.binaries is not None:
            for version in template.binaries.versions:
                kwds = {"method": "binaries", "version": version}
                p = pytest.param(
                    name,
                    kwds,
                    marks=[
                        pytest.mark.method_binaries,
                        getattr(pytest.mark, f"template_{name}"),
                    ],
                    id=name_kwds_to_id(name, kwds),
                )
                params.append(p)
        if template.source is not None:
            kwds = {"method": "source", "version": "latest"}
            p = pytest.param(
                name,
                kwds,
                marks=[
                    pytest.mark.method_source,
                    getattr(pytest.mark, f"template_{name}"),
                ],
                id=name_kwds_to_id(name, kwds),
            )
            params.append(p)
    return params


@pytest.mark.parametrize("template,template_kwds", get_template_params())
@pytest.mark.parametrize(
    "pkg_manager,base_image",
    [
        pytest.param("apt", "debian:buster-slim", marks=pytest.mark.pkg_manager_apt),
        pytest.param("yum", "centos:7", marks=pytest.mark.pkg_manager_yum),
    ],
)
@pytest.mark.parametrize(
    "builder",
    [
        pytest.param("docker", marks=pytest.mark.builds_docker),
        pytest.param("singularity", marks=pytest.mark.builds_singularity),
    ],
)
def test_one_template(
    record_property: ty.Callable[[str, ty.Any], None],
    tmp_path: Path,
    pkg_manager: str,
    base_image: str,
    builder: str,
    template: str,
    template_kwds: ty.Dict[str, str],
):
    method = template_kwds.get("method", "unknown")
    test_info = {
        "template": template,
        "method": method,
        "pkg_manager": pkg_manager,
        "base_image": base_image,
        "builder": builder,
        "template_kwds": template_kwds,
    }
    record_property("test_info", test_info)

    d = {
        "pkg_manager": pkg_manager,
        "instructions": [
            {"name": "from_", "kwds": {"base_image": base_image}},
            {"name": template, "kwds": template_kwds},
        ],
    }

    # TODO: add tests that confirm that package was installed properly

    if builder == "docker":
        renderer = DockerRenderer.from_dict(d)
        (tmp_path / "Dockerfile").write_text(str(renderer))
        with build_docker_image(context=tmp_path) as image:
            assert image
    elif builder == "singularity":
        renderer = SingularityRenderer.from_dict(d)
        (tmp_path / "Singularity").write_text(str(renderer))
        with build_singularity_image(context=tmp_path) as sif:
            assert sif.exists()
