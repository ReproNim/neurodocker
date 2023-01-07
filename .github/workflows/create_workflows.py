from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

apt_based = ["ubuntu:22.04", "ubuntu:18.04", "ubuntu:16.04"]
yum_based = ["centos:8", "fedora:36"]

softwares: dict[str, list[str]] = {
    "afni": {"versions": [], "methods": ["binaries", "source"]},
    "freesurfer": {"versions": ["7.3.1", "6.0.0"], "methods": []},
    "ants": {"versions": ["2.3.4", "2.0.0"], "methods": ["binaries", "source"]},
    "fsl": {"versions": ["6.0.5.1", "5.0.10"], "methods": ["binaries"]},
    "mrtrix3": {"versions": ["3.0.2", "3.0.0"], "methods": ["binaries", "source"]},
    "spm12": {"versions": ["r7771", "r6225"], "methods": ["binaries"]},
}

output_dir = Path(__file__).parent


def stringify_list(some_list: list[str]) -> str:
    if len(some_list) == 1:
        return f"'{some_list[0]}'"
    return "'" + "', '".join(some_list) + "'"


def main():

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("docker_build.jinja")

    os = {
        "apt_based": stringify_list(apt_based),
        "yum_based": stringify_list(yum_based),
        "all": stringify_list(apt_based + yum_based),
    }

    for software, spec in softwares.items():

        wf = {
            "header": "# This is file is automatically generated. Do not edit.",
            "os": os,
            "software": software,
        }

        if spec["versions"] and len(spec["versions"]) > 0:
            wf["add_version"] = "yup"
            wf["versions"] = stringify_list(spec["versions"])

        if spec["methods"] and len(spec["methods"]) > 0:
            wf["add_method"] = "yup"
            wf["methods"] = stringify_list(spec["methods"])

        print(wf)

        print(template.render(wf=wf))

        with open(output_dir.joinpath(software).with_suffix(".yml"), "w") as f:
            print(template.render(wf=wf), file=f)


if __name__ == "__main__":
    main()
