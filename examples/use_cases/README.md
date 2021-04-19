# Examples of common use-cases

This directory includes some examples of common use-cases for Docker containers generated with _Neurodocker_ from different stages of the analysis life cycle.

Each example:

- Generates a `Dockerfile` with _Neurodocker_ (using _Neurodocker_ Docker image and `debian:stretch` base image) that includes specific versions of FSL and ANTs
- Builds the Docker image
- Runs a short processing script (both Bash and Python examples included here). For these examples, we simply skull strip a T1-weighted image with BET and warp it into MNI space with ANTs.

### Important notes

- These example Docker images include FSL and ANTs in order to provide somewhat realistic examples. However, downloading FSL can take some time and the images will be quite large (~12GB).
- The commands in the example scripts likely will not produce good results and should not be used in any real analysis.

### Running examples

To run these examples, you will need Docker installed as we will use the _Neurodocker_ docker image. The _Neurodocker_ commands are explained in more detail at the end of this document.

To start, change directory to the cloned `use_cases` directory and create a directory for the output:

```shell
cd /path/to/cloned/use_cases
mkdir output
```

All the following commands assume they're being run from the `/path/to/cloned/use_cases` directory.

## Example 1

This example creates an image that contains some neuroimaging software and uses a custom Bash script to process the data, reading the script and the data from the local file system, and writing data back to the local file system.

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries > Dockerfile

# Build
docker build -t neurodocker-example:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}:/home \
    -v ${PWD}/input:/home/input \
    -v ${PWD}/output:/home/output \
    neurodocker-example:main \
    bash /home/processing_script.sh
```

## Example 2

As for example 1, however here we run a processing script written in Python that also requires some additional Python packages. For this example, we're installing `numpy` `pandas` and `nibabel` with `conda`. These packages are imported in the script for the sake of example, even though they aren't used.

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
    --miniconda \
        conda_install="python=3.6 pandas numpy nibabel" \
        create_env="analysis" \
        activate=true > Dockerfile
 
# Build
docker build -t neurodocker-example-py:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}:/home \
    -v ${PWD}/input:/home/input \
    -v ${PWD}/output:/home/output \
    neurodocker-example-py:main \
    python3 /home/processing_script.py
```

## Example 3

Here we will add the processing scripts to the Docker image and automatically run the processing script on data that is accessed from the local file system. This would allow someone to process data from their local file system with the processing script included in the Docker image.

### Bash

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
    --copy "processing_script.sh" "/home" \
    --add-to-entrypoint "bash /home/processing_script.sh" \
    --cmd "exit" > Dockerfile

# Build
docker build -t neurodocker-example:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}/input:/home/input \
    -v ${PWD}/output:/home/output \
    neurodocker-example:main
```

### Python

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
    --miniconda \
        conda_install="python=3.6 pandas numpy nibabel" \
        create_env="analysis" \
        activate=true \
    --copy "processing_script.py" "/home" \
    --add-to-entrypoint "python3 /home/processing_script.py" \
    --cmd "exit" > Dockerfile
 
# Build
docker build -t neurodocker-example-py:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}/input:/home/input \
    -v ${PWD}/output:/home/output \
    neurodocker-example-py:main
```

## Example 4

As for example 3, however here the processing script and the data are added to the Docker image. This would allow someone to simply `run` the Docker image to execute the processing script on the data that is included in the Docker image, still writing the output to the local file system to be inspected. This approach may be useful for someone who doesn't need to see the processing scripts or data and simply wants to run the pipeline, get a result, and check it against a published paper.

Note that although the processing scripts and input data are included in the Docker image, we still need to ensure that the output directory exists on our local file system and it needs to be mounted to the output directory of the Docker container (`-v ${PWD}/output:/home/output`).

### Bash

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
    --copy . "/home" \
    --run "mkdir -p /home/output" \
    --add-to-entrypoint "bash /home/processing_script.sh" \
    --cmd "exit" > Dockerfile

# Build
docker build -t neurodocker-example:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}/output:/home/output \
    neurodocker-example:main
```

### Python

```shell
# Generate Dockerfile
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
    --miniconda \
        conda_install="python=3.6 pandas numpy nibabel" \
        create_env="analysis" \
        activate=true \
    --copy . "/home" \
    --run "mkdir -p /home/output" \
    --add-to-entrypoint "python3 /home/processing_script.py" \
    --cmd "exit" > Dockerfile
 
# Build
docker build -t neurodocker-example-py:main .

# Run processing script
docker run -it --rm \
    -v ${PWD}/output:/home/output \
    neurodocker-example-py:main
```

## Components of _Neurodocker_ command

This component is common to all commands in these examples and simply selects the base image and the neuroimaging software to be included.

```shell
docker run --rm repronim/neurodocker:master generate docker \
    --base=debian:stretch \
    --pkg-manager=apt \
    --fsl version=6.0.4 method=binaries \
    --ants version=2.2.0 method=binaries \
```

The Miniconda distribution is used for Docker images where Python is also required. In these examples we install Python version 3.6 and also use the `conda` package manager to install the additional packages. We then create a virtual environment within the Docker container and activate it automatically.

```shell
    --miniconda \
        conda_install="python=3.6 pandas numpy nibabel" \
        create_env="analysis" \
        activate=true \
```

Next we copy the processing script (example 3) or the script and the data (example 4) to the Docker image.

```shell
# Copy script only
    --copy "processing_script.py" "/home" \

# Copy everything in current working directory (here, scripts and data)
    --copy . "/home" \
```

Make sure the output directory exists in the Docker image.

```shell
    --run "mkdir -p /home/output" \
```

Set the processing script to be run automatically when the Docker container is initiated and return to the local command line when finished. The container entrypoint are commands that are run automatically when the container is initiated. Therefore, we're adding a command to run the processing script to be executed when the container is initiated. The last `> Dockerfile` component writes the output of the _Neurodocker_ command to a file called `Dockerfile`.

```shell
    --add-to-entrypoint "python3 /home/processing_script.py" \
    --cmd "exit" > Dockerfile
```
