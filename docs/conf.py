# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from pathlib import Path

_here = Path(__file__).parent.absolute()
sys.path.insert(0, str(_here / ".."))
sys.path.insert(1, str(_here / "sphinxext"))

# from github_link import make_linkcode_resolve


# -- Project information -----------------------------------------------------

project = "Neurodocker"
copyright = "2017-2023, Neurodocker Developers"
author = "Neurodocker Developers"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxcontrib.apidoc",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "use_edit_page_button": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ReproNim/neurodocker",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Docker Hub",
            "url": "https://hub.docker.com/r/repronim/neurodocker",
            "icon": "fa-brands fa-docker",
        },
    ],
}


html_context = {
    "github_user": "ReproNim",
    "github_repo": "neurodocker",
    "github_version": "master",
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# -- Options for extensions ---------------------------------------------------

# Autodoc
# TODO: mocking click imports causes an error.
# autodoc_mock_imports = ["click", "jinja2"]
apidoc_module_dir = "../neurodocker"
apidoc_output_dir = "api"
apidoc_excluded_paths = ["conftest.py", "cli", "*/tests/*", "tests/*", "data/*"]
apidoc_separate_modules = True
apidoc_extra_args = ["--module-first", "-d 1", "-T"]

# Linkcode
# The following is used by sphinx.ext.linkcode to provide links to github
# linkcode_resolve = make_linkcode_resolve(
#     "neurodocker",
#     "https://github.com/ReproNim/neurodocker/blob/{revision}/"
#     "{package}/{path}#L{lineno}",
# )

# Sphinx-versioning
scv_show_banner = True

# Todo
todo_include_todos = True
