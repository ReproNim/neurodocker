In this directory you can find a `Dockerfile` with `FSL`.

The bash script `create_dockerfile.sh` contains a `neurodocker` command that was used to create the `Dockerfile`.

The `Dockerfile` contains:

 - using `neurodebian:stretch-non-free` as a base image
 - installing fsl and text editors
 - creating a user `neuro` and a home directory `/home/neuro`
 - setting `/home/neuro` as a working directory


You can test the script and `Dockerfile`

 - creating a `Dockerfile`: `bash create_dockerfile.sh`
 - building a Docker image: `docker build -t test/fsl .`
 - running a Docker container: `docker run -it --rm test/fsl`
 - within the container you can try to run `BET` command: `bet`
