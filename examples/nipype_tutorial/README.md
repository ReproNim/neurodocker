In this directory you can find a `Dockerfile` used to run [Nipype Tutorial](https://github.com/miykael/nipype_tutorial).

The bash script `create_dockerfile.sh` contains a `neurodocker` command that was used to create the `Dockerfile`.

The `Dockerfile` contains:

 - using `neurodebian:stretch-non-free` as a base image
 - installing ants, fsl, spm
 - creating a conda environment and installing various python library, including `nipype` from source
 - creating directory and changing permission
 - using datalad to download data
 - copying a current directory to the container
 - using `jupyter-notebook` as a default command