"""
This scripts uses a jinja template to create CI workflows to test.

    - different linux distributions (split by the package manager they use)
    - different softwares that neurodocker supports
    - different install method for a given software

All of those are defined in a python dictionary.

Versions to install are read from the neurodocker template for a given software.
It is possible to skip a version by adding a "skip_versions" key to the software.

Each workflow:

    - installs the latest version of neurodocker
    - builds a dockerfile for a combination of OS / software / version / install method
    - cat the dockerfile
    - attempts to build the corresponding image

This script will also create a "dashboard" saved in docs/README.md
to be picked up to be rendered by the github pages.
This requires for you to build the pages from the docs folder
and on the branch where the workflows are pushed to (currently "test_docker_build").

"""
from pathlib import Path

import yaml  # type: ignore
from jinja2 import Environment, FileSystemLoader, select_autoescape

apt_based = [
    "ubuntu:22.04",
    "ubuntu:18.04",
    "ubuntu:16.04",
    "debian:bullseye-slim",
    "debian:buster-slim",
    "debian:stretch-slim",
]
yum_based = ["fedora:36", "centos:7"]

"""
Add a "skip_versions" key to the software dictionary if you want to skip
testing a specific version. For example, if you want to skip testing
version 1.0.0 of afni, add the following to the software dictionary:

    "afni": {
            "skip_versions": ["1.0.0"],
            "methods": ["binaries", "source"],
            "afni_python": ["true", "false"],
        },

"""
softwares: dict[str, dict[str, list[str]]] = {
    "afni": {
        "methods": ["binaries", "source"],
        "afni_python": ["true", "false"],
    },
    "ants": {
        "methods": ["binaries", "source"],
    },
    "cat12": {"methods": ["binaries"]},
    "convert3d": {"methods": ["binaries"]},
    "dcm2niix": {
        "methods": ["binaries", "source"],
    },
    "freesurfer": {"methods": []},
    "fsl": {
        "methods": ["binaries"],
    },
    "matlabmcr": {
        "methods": ["binaries"],
    },
    "mricron": {"methods": ["binaries"]},
    "mrtrix3": {
        "methods": ["binaries", "source"],
    },
    "spm12": {"methods": ["binaries"]},
}

output_dir = Path(__file__).parent

template_folder = Path(__file__).parents[2].joinpath("neurodocker", "templates")

build_dashboard_file = Path(__file__).parents[2].joinpath("docs", "README.md")

# this has to match the name of the branch where the workflows are pushed to
# see .github/workflows/bootstrap.yml
branch = "test_docker_build"

# Update to match your username and repo name if you are testing things on your fork
# "ReproNim/neurodocker"
repo = "Remi-Gau/neurodocker"


def create_dashboard_file():
    """Create a build dashboard file."""

    print("creating build dashboard file...")
    print(build_dashboard_file)

    gh_actions_url = "http://github-actions.40ants.com/"

    with open(build_dashboard_file, "w") as f:

        image_base_url = f"{gh_actions_url}{repo}/matrix.svg?branch={branch}"
        print(
            """<!-- This page is generated automatically. Do not edit manually. -->
# Build dashboard
""",
            file=f)

        # table of content
        for software, _ in softwares.items():
            print(f"""- [{software}](#{software})""", file=f)

        print("", file=f)

        # link to the github actions workflow and image of the build status
        for software, _ in softwares.items():

            image_url = f"{image_base_url}&only={software}"
            print(
                f"""## {software}

[{software} workflow](https://github.com/{repo}/actions/workflows/{software}.yml)

![{software} build status]({image_url})
""",
                file=f,
            )


def get_versions_from_neurodocker_template(software: str) -> list[str]:
    """Load the list of versions to test from the software template."""
    template = template_folder.joinpath(software).with_suffix(".yaml")
    with open(template, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return list(data["binaries"]["urls"].keys())


def stringify(some_list: list[str]) -> str:
    if len(some_list) == 1:
        return f"'{some_list[0]}'"
    return "'" + "', '".join(some_list) + "'"


def main():

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        autoescape=select_autoescape(),
        lstrip_blocks=True,
        trim_blocks=True,
    )

    template = env.get_template("docker_build.jinja")

    os = {
        "apt_based": stringify(apt_based),
        "yum_based": stringify(yum_based),
        "all": stringify(apt_based + yum_based),
    }

    for software, spec in softwares.items():

        wf = {
            "header": "# This is file is automatically generated. Do not edit.",
            "os": os,
            "software": software,
        }

        versions = get_versions_from_neurodocker_template(software)
        for i in spec.get("skip_versions", []):
            versions.remove(i)

        if versions is not None and len(versions) > 0:
            wf["add_version"] = True
            wf["versions"] = stringify(versions)

        if spec.get("methods") is not None and len(spec["methods"]) > 0:
            wf["add_method"] = True
            wf["methods"] = stringify(spec["methods"])

        if spec.get("afni_python") is not None and len(spec["afni_python"]) > 0:
            wf["add_afni_python"] = True
            wf["afni_python"] = stringify(spec["afni_python"])

        output_file = output_dir.joinpath(software).with_suffix(".yml")
        print("creating workflow")
        print(f"{output_file}")
        with open(output_file, "w") as f:
            print(template.render(wf=wf), file=f)

    create_dashboard_file()


if __name__ == "__main__":
    main()
