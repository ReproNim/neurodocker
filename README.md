# Neurodocker

[![build status](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml/badge.svg)](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml)
[![docker pulls](https://img.shields.io/docker/pulls/repronim/neurodocker.svg)](https://hub.docker.com/r/repronim/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)
[![DOI](https://zenodo.org/badge/88654995.svg)](https://zenodo.org/badge/latestdoi/88654995)

_Neurodocker_ is a command-line program that generates custom Dockerfiles and Singularity recipes for neuroimaging and minifies existing containers.

Please see our website https://www.repronim.org/neurodocker for more information.

See our [list of supported software](https://www.repronim.org/neurodocker/user_guide/examples.html#supported-software)

## Build status

You can check the status of the build of the Docker images
for several of the neuroimaging software packages that are supported by _Neurodocker_
on [this page](https://github.com/ReproNim/neurodocker/blob/test_docker_build/docs/README.md). This may help with identifying base images that work well for your
use case.

## Base-image compatibility

Compatibility depends on the base image, software version, and installation method.
There is no single base image supported by every template. Consult the build results
linked above for the combination you plan to use.

Neurodocker warns on stderr when a template requests packages known to be unavailable
in the default repositories of official Debian 10–13 images. The check recognizes
codenames, numeric releases, point releases, and `-slim` tags, including Docker Hub
prefixes and tags with digests. It uses the current build stage's base image.

These are known limits of the binary templates, not a complete support matrix:

| Template | Debian 11, Bullseye | Debian 12, Bookworm | Debian 13, Trixie |
| --- | --- | --- | --- |
| MRtrix3 | Provides `libtiff5`, but 3.0.4 also needs a newer C++ runtime; use `method=source` | Missing `libtiff5`; use `method=source` | Missing `libtiff5`; use `method=source` |
| SPM12 | Missing `multiarch-support` | Missing `multiarch-support` | Missing `multiarch-support` and `libncurses5` |
| MATLAB Runtime | Missing `openjdk-8-jre` | Missing `openjdk-8-jre` | Missing `openjdk-8-jre` and `libncurses5` |

MRtrix3's precompiled binaries require `libtiff.so.5`. Installing `libtiff6` does
not supply that ABI. For MRtrix3 3.0.4 binaries, `ubuntu:22.04` provides both
`libtiff5` and the required C++ runtime. SPM12 also installs a legacy `libxp6` package that depends on
`multiarch-support`, so deleting that dependency alone does not fix its installation.

Warnings do not stop generation: a recipe may supply dependencies through additional
repositories or earlier instructions. Neurodocker does not inspect custom images,
resolve floating tags such as `latest`, or query package repositories during generation.
No warning does not guarantee a successful build, and package availability does not
guarantee runtime compatibility. Ubuntu and other distributions are not covered by
this check. Build and test your chosen combination before using it.

Keep diagnostics separate from generated recipes:

```shell
neurodocker generate docker -p apt --base-image debian:bookworm \
  --mrtrix3 version=3.0.4 method=source > Dockerfile
```

# Installation

Use the _Neurodocker_ Docker image (recommended):

```shell
docker run --rm repronim/neurodocker:latest --help
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
python -m pip install --no-cache-dir --editable . --group dev
```

Before committing changes, initialize `prek` with `prek install`, or `pre-commit` with `pre-commit install`. This will format code with each commit to keep the style consistent. _Neurodocker_ uses `ruff` for formatting.
