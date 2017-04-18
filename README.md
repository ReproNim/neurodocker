# neurodocker
[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates Docker images with specified versions of Python and neuroimaging software. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces.


Example
-------

The following code block creates a Docker image of Ubuntu 16.04 and Miniconda, and runs a command within the resulting Docker container. Specifically, this code uses [this JSON file](samples/json_files/ubuntu-16.04_py-3.5.1.json) to generate [this Dockerfile](samples/ubuntu-16.04_py-3.5.1/Dockerfile). With the help of [docker-py](https://github.com/docker/docker-py), a Docker image is built using the saved Dockerfile. While building, [this JSON file](samples/ubuntu-16.04_py-3.5.1/conda-env.json) is used to create a `conda` environment with the specified Python version and packages. Finally, a command is run within the resulting container.

```python
from src.docker import SpecsParser, Dockerfile, DockerImage

specs_file = "samples/json_files/ubuntu-16.04_py-3.5.1.json"
path_to_build = "samples/ubuntu-16.04_py-3.5.1"
command = 'python -c "import numpy; print(numpy.__version__)"'
specs = SpecsParser(filepath=specs_file)

# Generate Dockerfile.
d = Dockerfile(specs.specs, path_to_build, deps_method="apt-get")
d.create()  # Combine Dockerfile instructions into a single string.
d.save()  # Save string to file `path_to_build/Dockerfile

# Build image using the saved Dockerfile, and run command within it.
image = DockerImage(path=path_to_build)
image.run(command)
image._get_console_output()  # Returns '1.12.1'
```
