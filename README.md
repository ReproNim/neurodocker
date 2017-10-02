# Neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates custom Dockerfiles for neuroimaging and minifies existing Docker images (using [ReproZip](https://www.reprozip.org/)). The package can be used from the command-line or within a Python script. The command-line interface generates Dockerfiles and minifies Docker images, but interaction with the Docker Engine is left to the various `docker` commands. Within a Python script, however, _Neurodocker_ can generate Dockerfiles, build Docker images, run commands within resulting containers (using the [`docker` Python package](https://github.com/docker/docker-py)), and minify Docker images. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces.

Examples:
  - Command-line
    - [Generate Dockerfile](#generate-dockerfile)
    - [Generate Dockerfile (full)](#generate-dockerfile-full)
  - In a Python script
    - [Generate Dockerfile, build Docker image, run commands in image (minimal)](#generate-dockerfile-build-docker-image-run-commands-in-image-minimal)
    - [Generate full Dockerfile](#generate-full-dockerfile)
      - [Generated Dockerfile](examples/generated-full.Dockerfile)
  - Minimize Docker image
    - [Minimize existing Docker image](#minimize-existing-docker-image)
    - [Example of minimizing Docker image for FreeSurfer recon-all](https://github.com/freesurfer/freesurfer/issues/70#issuecomment-316361886)


# Note to users

This software is still in the early stages of development. If you come across an issue or a way to improve _Neurodocker_, please submit an issue or a pull request.


# Installation

You can use _Neurodocker's_ Docker image, or you can install the project with `pip`:

`docker run --rm kaczmarj/neurodocker --help`

or

```shell
pip install https://github.com/kaczmarj/neurodocker/archive/master.tar.gz
neurodocker --help
```

Note that building and minifying Docker images is not possible within the _Neurodocker_ Docker image.


# Supported Software

Valid options for each software package are the keyword arguments for the class that installs that package. These classes live in [`neurodocker.interfaces`](neurodocker/interfaces/). The default installation behavior for every software package (except Miniconda) is to install by downloading and un-compressing the binaries.


| software | argument | description |
| -------- | -------- | ----------- |
| **AFNI** | version* | Either 17.2.02 or latest. |
| **ANTs** | version* | 2.2.0, 2.1.0, 2.0.3, or 2.0.0 |
|          | use_binaries | If true (default), use pre-compiled binaries. If false, build from source. |
|          | git_hash  | Git hash to checkout to before building from source (only used if use_binaries is false). |
| **FreeSurfer** | version* | Any version for which binaries are provided. |
|                | license_path | Relative path to license file. If provided, this file will be copied into the Docker image. Must be within the build context. |
|                | min | If true, install a version of FreeSurfer minimized for recon-all. See [freesurfer/freesurfer#70](https://github.com/freesurfer/freesurfer/issues/70). False by default. |
| **FSL**** | version* | Any version for which binaries are provided. |
|           | eddy_5011 | If true, use pre-release version of FSL eddy v5.0.11 |
|           | eddy_5011_cuda | 6.5, 7.0, 7.5, 8.0; only valid if using eddy pre-release |
|           | use_binaries | If true (default), use pre-compiled binaries. Building from source is not available now but might be added in the future. |
|           | use_installer | If true, use FSL's Python installer. Only valid on CentOS images. |
| **MINC** | version* | 1.9.15 |
| **Miniconda** | env_name* | Name of this conda environment. |
|               | yaml_file | Environment specification file. Can be path on host or URL. |
|               | conda_install | Packages to install with conda. e.g., `conda_install="python=3.6 numpy traits"` |
|               | pip_install | Packages to install with pip. |
|               | conda_opts  | Command-line options to pass to [`conda create`](https://conda.io/docs/commands/conda-create.html). e.g., `conda_opts="-c vida-nyu"` |
|               | pip_opts    | Command-line options to pass to [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#options). |
|               | add_to_path | If true (default), add this environment to $PATH. |
|               | miniconda_version | Version of Miniconda. Latest by default. |
| **MRtrix3** | use_binaries | If true (default), use pre-compiled binaries. If false, build from source. |
|             | git_hash | Git hash to checkout to before building from source (only used if use_binaries is false). |
| **NeuroDebian** | os_codename* | Codename of the operating system (e.g., stretch, zesty). |
|                 | download_server* | Server to download NeuroDebian packages from. Choose the one closest to you. See `neurodocker generate --help` for the full list of servers. |
|                 | pkgs | Packages to download from NeuroDebian. |
|                 | full | If true (default), use non-free sources. If false, use libre sources. |
| **PETPVC** | version* | 1.2.0-b, 1.2.0-a, 1.1.0, 1.0.0 |
| **SPM** | version*        | 12 (earlier versions will be supported in the future). |
|         | matlab_version* | R2017a (other MCR versions will be supported once earlier SPM versions are supported). |


\* required argument.

** FSL is non-free. If you are considering commercial use of FSL, please consult the [relevant license](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Licence).


# Examples

## Generate Dockerfile

Generate Dockerfile, and print result to stdout. The result can be piped to `docker build` to build the Docker image.

```shell
docker run --rm kaczmarj/neurodocker generate -b ubuntu:17.04 -p apt --ants version=2.2.0

docker run --rm kaczmarj/neurodocker generate -b ubuntu:17.04 -p apt --ants version=2.2.0 | docker build -
```

## Generate Dockerfile (full)

In this example, a Dockerfile is generated with all of the software that _Neurodocker_ supports, and the Dockerfile is saved to disk. The order in which the arguments are given is preserved in the Dockerfile. The saved Dockerfile can be passed to `docker build`.

```shell
# Generate Dockerfile.
docker run --rm kaczmarj/neurodocker generate \
--base debian:stretch --pkg-manager apt \
--arg FOO=BAR BAZ \
--install git vim \
--afni version=latest \
--ants version=2.2.0 \
--freesurfer version=6.0.0 min=true \
--fsl version=5.0.10 \
--minc version=1.9.15 \
--user=neuro \
--miniconda env_name=neuro \
            conda_opts="--channel vida-nyu" \
            conda_install="python=3.5.1 numpy pandas reprozip traits" \
            pip_install="nipype" \
            add_to_path=true \
--miniconda env_name=neuro \
            pip_install="pylsl" \
--miniconda env_name=py27 \
            conda_install="python=2.7" \
--user=root \
--mrtrix3 \
--neurodebian os_codename="jessie" \
              download_server="usa-nh" \
              pkgs="dcm2niix git-annex-standalone" \
--petpvc version=1.2.0-b \
--spm version=12 matlab_version=R2017a \
--user=neuro \
--env KEY_A=VAL_A KEY_B=VAL_B \
--env KEY_C="based on \$KEY_A" \
--instruction='RUN mkdir /opt/mydir' \
--run-bash="echo 'myfile' > /tmp/myfile.txt" \
--add-to-entrypoint 'echo hello world' 'source myfile.sh' \
--cmd arg1 arg2 \
--volume /var /tmp \
--expose 8888 80 \
--label FOO=BAR BAZ=CAT \
--workdir /home/neuro \
--no-check-urls > examples/generated-full.Dockerfile

# Build Docker image using the saved Dockerfile.
docker build -t myimage -f generated-full.Dockerfile examples
```

Here is the [Dockerfile](examples/generated-full.Dockerfile) generated by the command above.


## Generate Dockerfile, build Docker image, run commands in image (minimal)

In this example, a dictionary of specifications is used to generate a Dockerfile. A Docker image is built from the string representation of the Dockerfile. A container is started from that container, and commands are run within the running container. When finished, the container is stopped and removed.


```python
from neurodocker import Dockerfile
from neurodocker.docker import DockerImage, DockerContainer

specs = {
    'pkg_manager': 'apt',
    'check_urls': False,
    'instructions': [
        ('base', 'ubuntu:17.04'),
        ('ants', {'version': '2.2.0'})
    ]
}
# Create Dockerfile.
df = Dockerfile(specs)

# Build image.
image = DockerImage(df).build(log_console=False, log_filepath="build.log")

# Start container, and run commands.
container = DockerContainer(image).start()
container.exec_run('antsRegistration --help')
container.exec_run('ls /')
container.cleanup(remove=True)
```


## Generate full Dockerfile

In this example, we create a Dockerfile with all of the software that _Neurodocker_ supports, and we supply arbitrary Dockerfile instructions.

```python
from neurodocker import Dockerfile

specs = {
    'pkg_manager': 'apt',
    'check_urls': False,
    'instructions': [
        ('base', 'ubuntu:17.04'),
        ('install', ['git', 'vim']),
        ('user', 'neuro'),
        ('miniconda', {
            'env_name': 'my_env',
            'conda_install': 'python=3.5.1 traits',
            'pip_install': 'https://github.com/nipy/nipype/archive/master.tar.gz'}),
        ('user', 'root'),
        ('afni', {'version': 'latest'}),
        ('ants', {'version': '2.2.0'}),
        ('freesurfer', {'version': '6.0.0', 'license_path': 'rel/path/license.txt'}),
        ('fsl', {'version': '5.0.10', 'use_binaries': True}),
        ('mrtrix3', {'use_binaries': False}),
        ('neurodebian', {'os_codename': 'zesty', 'download_server': 'usa-nh',
                         'pkgs': ['afni', 'dcm2niix']}),
        ('spm', {'version': '12', 'matlab_version': 'R2017a'}),
        ('instruction', 'RUN echo "Hello, World"'),
        ('copy', ['rel/path/to/startup.sh', '/path/in/container/']),
        ('user', 'neuro'),
        ('env', {'KEY_A': 'VAL_A', 'KEY_B': 'VAL_B is "hello"'}),
        ('env', {'KEY_C': 'based on $KEY_A'}),
    ]
}

df = Dockerfile(specs)
df.save('path/to/Dockerfile')
print(df)
```


## Minimize existing Docker image

In the following example, a Docker image is built with ANTs version 2.2.0 and a functional scan. The image is minified for running `antsMotionCorr`. The original ANTs Docker image is 1.85 GB, and the "minified" image is 365 MB.

```shell
# Create a Docker image with ANTs, and download a functional scan.
download_cmd="RUN curl -sSL -o /home/func.nii.gz http://psydata.ovgu.de/studyforrest/phase2/sub-01/ses-movie/func/sub-01_ses-movie_task-movie_run-1_bold.nii.gz"
neurodocker generate -b centos:7 -p yum --ants version=2.2.0 --instruction="$download_cmd" | docker build -t ants:2.2.0 -

# Run the container.
docker run --rm -it --name ants-reprozip-container --security-opt=seccomp:unconfined ants:2.2.0

# (in a new terminal window)
# Output a ReproZip pack file in ~/neurodocker-reprozip-output with the files
# necessary to run antsMotionCorr.
# See https://github.com/stnava/ANTs/blob/master/Scripts/antsMotionCorrExample
cmd="antsMotionCorr -d 3 -a /home/func.nii.gz -o /home/func_avg.nii.gz"
neurodocker reprozip-trace ants-reprozip-container "$cmd"

reprounzip docker setup neurodocker-reprozip.rpz test
```
