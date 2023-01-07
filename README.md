# Neurodocker

[![build status](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml/badge.svg)](https://github.com/ReproNim/neurodocker/actions/workflows/pull-request.yml)
[![docker pulls](https://img.shields.io/docker/pulls/repronim/neurodocker.svg)](https://hub.docker.com/r/repronim/neurodocker/)
[![docker pulls](https://img.shields.io/docker/pulls/kaczmarj/neurodocker.svg)](https://hub.docker.com/r/kaczmarj/neurodocker/)
[![python versions](https://img.shields.io/pypi/pyversions/neurodocker.svg)](https://pypi.org/project/neurodocker/)
[![DOI](https://zenodo.org/badge/88654995.svg)](https://zenodo.org/badge/latestdoi/88654995)

_Neurodocker_ is a command-line program that generates custom Dockerfiles and Singularity recipes for neuroimaging and minifies existing containers.

Please see our website https://www.repronim.org/neurodocker for more information.

# image build status

[![afni](https://github.com/Remi-Gau/neurodocker/actions/workflows/afni.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/afni.yml)
[![ants](https://github.com/Remi-Gau/neurodocker/actions/workflows/ants.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/ants.yml)
[![freesurfer](https://github.com/Remi-Gau/neurodocker/actions/workflows/freesurfer.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/freesurfer.yml)
[![fsl](https://github.com/Remi-Gau/neurodocker/actions/workflows/fsl.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/fsl.yml)
[![mrtrix3](https://github.com/Remi-Gau/neurodocker/actions/workflows/mrtrix3.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/mrtrix3.yml)
[![spm12](https://github.com/Remi-Gau/neurodocker/actions/workflows/spm12.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/spm12.yml)
[![matlabmcr](https://github.com/Remi-Gau/neurodocker/actions/workflows/matlabmcr.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/matlabmcr.yml)
[![cat12](https://github.com/Remi-Gau/neurodocker/actions/workflows/cat12.yml/badge.svg)](https://github.com/Remi-Gau/neurodocker/actions/workflows/cat12.yml)

# Installation

Use the _Neurodocker_ Docker image (recommended):

```shell
docker run --rm kaczmarj/neurodocker:0.9.1 --help
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
