# conda python example

In this directory you can find a `Dockerfile` and `Singularity` file with a conda python environment.

The shell script `generate.sh` contains a `neurodocker` command that creates the `Dockerfile` and `Singularity` file.

Both specs:

 - use `neurodebian:stretch-non-free` as the base image
 - install text editors
 - create a conda environment and installing various python library including jupyter-notebook; most of the libraries are installed using `conda`, and `nilearn` is installed using a `pip` command; the environment will be automatically activated
 - change the jupyter configuration, so you'll be able to open notebooks locally

The Dockerfile uses `jupyter-notebook` as the default command. The Singularity file will start a bash shell by default.


## Docker

```shell
# Generate Dockerfile
$ ./generate.sh
# Build Docker image
$ docker build -t test/conda .
# Run the container (start jupyter notebook)
$ docker run --rm -it -p 8888:8888 test/conda
# Start interactive bash shell
$ docker run --rm -it test/conda bash
```

## Singularity

```shell
# Generate Singularity file
$ ./generate.sh
# Build Singularity image
$ singularity build jupyter.sqsh Singularity
# Run the container (start jupyter notebook)
$ singularity run jupyter.sqsh jupyter-notebook
# Start interactive bash shell
$ singularity run jupyter.sqsh
```
