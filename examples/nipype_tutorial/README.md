In this directory you can find a `Dockerfile` used to run [Nipype Tutorial](https://github.com/miykael/nipype_tutorial).

The bash script `create_dockerfile.sh` contains a `neurodocker` command that was used to create the `Dockerfile`.

The `Dockerfile` contains:

 - using `neurodebian:stretch-non-free` as a base image
 - installing ants, fsl, spm
 - creating a conda environment and installing various python library, including `nipype` from source
 - creating directory and changing permission
 - using datalad to download data
 - copying a current directory to the container (so don't expect the [Nipype Tutorial notebooks](https://github.com/miykael/nipype_tutorial/tree/master/notebooks) if you're not in the specific directory)
 - using `jupyter-notebook` as a default command


You can test the script and `Dockerfile`

 - creating a `Dockerfile`: `bash create_dockerfile.sh`
 - building a Docker image (this will take a while): `docker build -t test/nipype_tutorial .`
 - running a Docker container: `docker run -it --rm -p8888:8888 test/nipype_tutorial jupyter-notebook`
 - container should start `jupyter-notebook`, you can copy the link and paste to your browser
