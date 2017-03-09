# nipype-regtests

Regression testing on nipype's interfaces

The `samples` directory contains folders with sample Dockerfiles.



To-do
-----

- [x] create Dockerfiles automatically
- [ ] set up testing for Dockerfiles
- [ ] automatically build Docker image from Dockerfile
- [ ] run code in Docker container (include mounts)
- [ ] extract code output
- [ ] compare code output among matrix



Example
-------

The following block uses [this YAML file](samples/gen-xenial-py35.yml) to generate [this Dockerfile](samples/gen-xenial-py35/Dockerfile).

```python
from src.dockerfile.dockerfile import Dockerfile
from src.dockerfile.utils import SpecsParser

filepath = "samples/gen-xenial-py35.yml"
specs = SpecsParser(filepath=filepath)

d = Dockerfile(specs.specs, "samples/gen-xenial-py35", deps_method="apt-get")
d.save()
```
