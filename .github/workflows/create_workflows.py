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

        print(wf)

        print(template.render(wf=wf))

        with open(output_dir.joinpath(software).with_suffix(".yml"), "w") as f:
            print(template.render(wf=wf), file=f)


if __name__ == "__main__":
    main()
