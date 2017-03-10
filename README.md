# nipype-regtests

Regression testing on nipype's interfaces

The `samples` directory contains folders with sample Dockerfiles.



To-do
-----

- [x] create Dockerfiles automatically
- [ ] set up tests for Dockerfile creation
- [x] automatically build Docker image from Dockerfile
- [x] run code in Docker container (include mounts)
- [x] extract code output
- [ ] compare code output among matrix



Example
-------

The following code block creates a Docker image of Ubuntu 16.04 and Miniconda, and runs a command within the resulting Docker container. Specifically, this code uses [this YAML file](samples/gen-xenial-py35.yml) to generate [this Dockerfile](samples/gen-xenial-py35/Dockerfile). With the help of [docker-py](https://github.com/docker/docker-py), a Docker image is built using the saved Dockerfile, and a command is run within the resulting container.

```python
from src.docker import SpecsParser, Dockerfile, DockerImage

specs_file = "samples/gen-xenial-py35.yml"
path_to_build = "samples/gen-xenial-py35"
command = 'python -c "import numpy; print(numpy.__version__)"'
specs = SpecsParser(filepath=specs_file)

# Generate Dockerfile.
d = Dockerfile(specs.specs, path_to_build, deps_method="apt-get")
d.create()  # Combine Dockerfile instructions into a single string.
d.save()  # Save string to file `path_to_build`/Dockerfile

# Build image using the saved Dockerfile, and run command within it.
image = DockerImage(path=path_to_build)
image.run(command)
image._get_console_output()  # Returns '1.12.0'
```
