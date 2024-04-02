"""Print list of software packages to be included in the documentation.

Read them from the registered yml templates.
"""

from pathlib import Path

from neurodocker.reproenv.state import registered_templates_items

output_file = Path(__file__).parent / "user_guide" / "examples.rst"

software = {"name": [], "url": []}
for s in registered_templates_items():
    if s[1]["name"] == "_header":
        continue
    software["name"].append(s[1]["name"])
    software["url"].append(s[1]["url"])

with open(output_file, "r") as f:
    lines = f.readlines()

with open(output_file, "w") as f:
    print_list = False

    for line in lines:
        if line.startswith(".. INSERT LIST START"):
            print_list = True
            f.write(line)
            f.write("\n")
            for s in sorted(zip(software["name"], software["url"])):
                f.write(f"- `{s[0]} <{s[1]}>`_\n")
            f.write("\n")
        if line.startswith(".. INSERT LIST END"):
            print_list = False

        if not print_list:
            f.write(line)
