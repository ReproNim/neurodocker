In this directory you can find a `Dockerfile` and `Singularity` file used to run [Nipype Tutorial](https://github.com/miykael/nipype_tutorial).

The shell script `generate.sh` contains a `neurodocker` command that was used to create the `Dockerfile` and `Singularity` file.

Both specs:

 - use `neurodebian:stretch-non-free` as a base image
 - install ants, fsl, spm
 - create a conda environment and install various python library, including `nipype` from source
 - create directory and changing permission
 - use datalad to download data
 - copy a current directory to the container (so don't expect the [Nipype Tutorial notebooks](https://github.com/miykael/nipype_tutorial/tree/master/notebooks) if you're not in the specific directory)

The `Dockerfile` sets `jupyter-notebook` as the default command. The `Singularity` file will run a bash shell by default.


## Docker

```shell
# Generate Dockerfile
$ ./generate.sh
# Build Docker image
$ docker build -t test/nipype_tutorial .
# Start jupyter-notebook
$ docker run -it --rm -p8888:8888 test/nipype_tutorial
# Start interactive bash shell
$ docker run -it --rm test/nipype_tutorial bash
```

## Singularity

```shell
# Generate Singularity file
$ ./generate.sh
# Build Singularity image
$ singularity build nipype_tutorial.sqsh Singularity
# Start jupyter-notebook
$ singularity run nipype_tutorial.sqsh jupyter-notebook
# Start interactive bash shell
$ singularity run nipype_tutorial.sqsh
```
