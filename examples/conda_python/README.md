In this directory you can find a `Dockerfile` with conda python environment.

The bash script `create_dockerfile.sh` contains a `neurodocker` command that was used to create the `Dockerfile`.

The `Dockerfile` contains:

 - using `neurodebian:stretch-non-free` as a base image
 - installing text editors
 - creating a conda environment and installing various python library including jupyter-notebook; most of the libraries are installed using `conda`, and `nilearn` is installed using a `pip` command, the environment will be automatically activated
 - changing a jupyter configuartion, so you'll be able to open a notebook locally
 - creating directory and changing permission
 - copying a current directory to the container
 - using `jupyter-notebook` as a default command


You can test the script and `Dockerfile`

 - creating a `Dockerfile`: `bash create_dockerfile.sh`
 - building a Docker image (this will take a few minutes): `docker build -t test/conda .`
 - running a Docker container: `docker run -it --rm -p8888:8888 test/conda` (container should start `jupyter-notebook`, you can copy the link and paste to your browser)
 - you can still start container with `bash` instead of `jupyter-notebook`: `docker run -it --rm test/conda bash`
 