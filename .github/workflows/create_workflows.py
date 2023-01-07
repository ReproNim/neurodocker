from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

apt_based = ["ubuntu:22.04", "ubuntu:18.04", "ubuntu:16.04"]
yum_based = ["centos:8", "fedora:36"]

softwares: dict[str, list[str]] = {"afni": []}

output_dir = Path(__file__).parent

def stringify_list(some_list: list[str]) -> str:
    return "'" + "', '".join(some_list) + "'"


def main():

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent), autoescape=select_autoescape()
    )

    template = env.get_template("docker_build.jinja")

    os = {
        "apt_based": stringify_list(apt_based),
        "yum_based": stringify_list(yum_based),
        "all": stringify_list(apt_based + yum_based),
    }

    for software, versions in softwares.items():

        if versions and len(versions) > 0:
            wf = {
                "os": os,
                "software": software,
                "add_version": 'yup',
                "versions": stringify_list(versions),
            }
        else:
            wf = {
                "os": os,
                "software": software
            }

        print(wf)

        print(template.render(wf=wf))

        with open(output_dir.joinpath(software).with_suffix('.yml'), 'w') as f:
            print(template.render(wf=wf), file=f)


if __name__ == "__main__":
    main()
