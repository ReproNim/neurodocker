"""Generate the file neurodocker/docs/build_results.py"""

import json
from pathlib import Path

import jinja2

# neurodocker/docs/build_results.rst
output = Path(__file__).parent.parent / "build_results.rst"

with (Path(__file__).parent / "build_results.json").open("r") as f:
    report = [json.loads(line) for line in f]

# Get reports we care about.
test_reports = [
    r for r in report if r["$report_type"] == "TestReport" and r["when"] == "call"
]

# List of dicts like
# {'pkg_manager': 'apt',
#  'base_image': 'debian:buster-slim',
#  'builder': 'docker',
#  'template': '_header',
#  'template_kwds': {'method': 'source', 'version': 'latest'},
#  'outcome': 'passed'}
build_results = [
    {**tr["user_properties"][0][1], "outcome": tr["outcome"]} for tr in test_reports
]

# Add emojis for outcomes.
outcome_symbols = {
    "passed": "🟢",
    "failed": "🔴",
}

for d in build_results:
    this_symbol = outcome_symbols.get(d["outcome"], "🟡")
    d["outcome_symbol"] = this_symbol


tmpl = """\
Build Results
=============

The table below lists the build results for the templates included in Neurodocker.
These builds are parameterized over many variables, including version, package manager,
base image, builder (Docker or Singularity), and installation method (binaries or
source).

| 🟢 = passed
| 🔴 = failed
| 🟡 = unknown

.. list-table:: Build results
   :header-rows: 1

   * - outcome
     - template
     - method
     - arguments
     - package manager
     - base image
     - builder
   {% for d in build_results -%}
   * - {{ d["outcome_symbol"] }}
     - {{ d["template"] }}
     - {{ d["method"] }}
     {% for k, v in d["template_kwds"].items() %}
     {%- if loop.first %}- {% else %}  {% endif -%}
       | {{ k }}="{{ v }}"
     {% endfor -%}
     - {{ d["pkg_manager"] }}
     - {{ d["base_image"] }}
     - {{ d["builder"] }}
   {% endfor -%}

"""


def render_build_results() -> str:
    t = jinja2.Template(tmpl)
    # TODO: how can we reverse sort by version?
    # TODO: omit _header.
    build_results.sort(key=lambda d: (d["template"], d["template_kwds"].get("version")))
    return t.render(build_results=build_results)


if __name__ == "__main__":
    rendered = render_build_results()
    output.write_text(rendered)
