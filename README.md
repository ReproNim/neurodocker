# Neurodocker

[![build status](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml/badge.svg)](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml)
[![docker pulls](https://img.shields.io/docker/pulls/repronim/neurodocker.svg)](https://hub.docker.com/r/repronim/neurodocker/)
[![docker pulls](https://img.shields.io/docker/pulls/kaczmarj/neurodocker.svg)](https://hub.docker.com/r/kaczmarj/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)
[![DOI](https://zenodo.org/badge/88654995.svg)](https://zenodo.org/badge/latestdoi/88654995)

_Neurodocker_ is a command-line program that generates custom Dockerfiles and Singularity recipes for neuroimaging and minifies existing containers.

Please see our website https://www.repronim.org/neurodocker for more information.

# Installation

Use the _Neurodocker_ Docker image (recommended):

```shell
docker run --rm repronim/neurodocker:0.7.0 --help
```

The Docker images were moved to [repronim/neurodocker](https://hub.docker.com/r/repronim/neurodocker) from [kaczmarj/neurodocker](https://hub.docker.com/r/kaczmarj/neurodocker).

This project can also be installed with `pip`:

```shell
pip install neurodocker
neurodocker --help
```

If the `pip install` command above gives a permissions error, install as a non-root user:

```shell
pip install --user neurodocker
```

_Note_: it is not yet possible to minimize Docker containers using the _Neurodocker_ Docker image.


# Developer installation

Clone the repository and install in editable mode.

```
git clone https://github.com/ReproNim/neurodocker
cd neurodocker
python -m pip install --no-cache-dir --editable .[all]
```

Before committing changes, initialize `pre-commit` with `pre-commit install`. This will format code with each commit to keep the style consistent. _Neurodocker_ uses `black` for formatting.
