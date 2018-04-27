# FSL

In this directory you can find a `Dockerfile` and `Singularity` file with `FSL`.

The shell script `generate.sh` contains a `neurodocker` command that was used to create both files.

Both specs:

 - use `neurodebian:stretch-non-free` as a base image
 - install fsl and text editors
 - create a non-root user `neuro` and a home directory `/home/neuro`
 - set `/home/neuro` as a working directory

## Docker

```shell
# Generate Dockerfile
$ ./generate.sh
# Build Docker image
$ docker build -t test/fsl .
# Start an interactive bash shell
$ docker run --rm -it test/fsl
# Run bet inside the container
(in-container)$ bet
```

## Singularity

```shell
# Generate Singularity file
$ ./generate.sh
# Build Singularity image
$ singularity build fsl.sqsh Singularity
# Start interactive bash shell
$ singularity run fsl.sqsh
# Run bet inside the container
(in-container)$ bet
```
