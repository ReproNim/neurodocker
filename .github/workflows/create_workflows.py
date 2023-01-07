from pathlib import Path

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

softwares: dict[str, dict[str, list[str]]] = {
    "afni": {
        "versions": [],
        "methods": ["binaries", "source"],
        "afni_python": ["true", "false"],
    },
    "freesurfer": {"versions": ["7.3.1", "7.2.0", "7.1.0", "6.0.0"], "methods": []},
    "ants": {
        "versions": ["2.3.4", "2.2.0", "2.0.0"],
        "methods": ["binaries", "source"],
    },
    "fsl": {"versions": ["6.0.5.1", "6.0.0", "5.0.10"], "methods": ["binaries"]},
    "mrtrix3": {
        "versions": ["3.0.2", "3.0.1", "3.0.0"],
        "methods": ["binaries", "source"],
    },
    "matlabmcr": {"versions": ["2021b", "2015a", "2010a"], "methods": ["binaries"]},
    "spm12": {"versions": ["r7771", "r6914", "r6225"], "methods": ["binaries"]},
    "cat12": {"versions": ["r1933_R2017b"], "methods": ["binaries"]},
}

output_dir = Path(__file__).parent


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

        if spec.get("versions") is not None and len(spec["versions"]) > 0:
            wf["add_version"] = True
            wf["versions"] = stringify(spec["versions"])

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
