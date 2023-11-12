Add software to Neurodocker
===========================

Neurodocker defines the instructions to install and configure software using YAML files.
These files are known as *templates*. This page explains how to add a new template to
Neurodocker.

The :code:`env` and :code:`instructions` values can use
`Jinja2 <https://jinja.palletsprojects.com/en/2.11.x/templates/>`_ template language.

Example specification
---------------------

This example installs :code:`jq`, a
`command-line JSON processor <https://github.com/stedolan/jq>`_.

.. code-block:: yaml

    # The name of the software. This becomes the name in the template registry.
    # The CLI option would be rendered as `--jq`.
    name: jq
    url: https://jqlang.github.io/jq/
    # An alert that is printed when using this template in the CLI.
    alert: Please be advised that this software uses
    # How to install this software from pre-compiled binaries.
    binaries:
      # The available versions and their corresponding urls.
      urls:
        "1.6": https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
        "1.5": https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
      # Arguments that the user can provide when using this template. These arguments
      # should be referenced in the `env` and/or `instructions`.
      arguments:
        required:
        - version
        optional:
          install_path: /opt/jq-{{ self.version }}
      # Environment variables to set in the container. Keys and values must be strings.
      env:
        PATH: {{ self.install_path }}:$PATH
      # System packages that this software depends on.
      dependencies:
        apt:
        - ca-certificates
        - curl
        yum:
        - curl
      # The installation instructions. Think of this like a shell scripts that installs
      # the software.
      instructions: |
        {{ self.install_dependencies() }}
        mkdir -p {{ self.install_path }}
        curl -fsSL --output {{ self.install_path }}/jq {{ self.urls[self.version]}}
        chmod +x {{ self.install_path }}/jq
