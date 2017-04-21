# neurodocker

[![Build Status](https://travis-ci.org/kaczmarj/neurodocker.svg?branch=master)](https://travis-ci.org/kaczmarj/neurodocker)
[![codecov](https://codecov.io/gh/kaczmarj/neurodocker/branch/master/graph/badge.svg)](https://codecov.io/gh/kaczmarj/neurodocker)


_Neurodocker_ is a Python project that generates Docker images with specified versions of Python and neuroimaging software. The project is used for regression testing of [Nipype](https://github.com/nipy/nipype/) interfaces. See the [example](#example) at the bottom of this page.



## Supported Software

This list is growing.

### ANTs

To install, include `'ants'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'ants'` are keywords for [`neurodocker.interfaces.ANTs`](neurodocker/interfaces/ants.py#L27). Binaries can be installed (compiled on CentOS 5), or ANTs can be compiled from source.

### Conda

To install, include `'conda_env'` in the specifications dictionary. Valid keys within `'conda_env'` are keywords for [`neurodocker.interfaces.Miniconda`](neurodocker/interfaces/miniconda.py#L12). The `conda-forge` channel is added by default.

### FSL

To install, include `'fsl'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'fsl'` are keywords for [`neurodocker.interfaces.FSL`](neurodocker/interfaces/fsl.py#L11). Beware that FSL's Python installer will panic if used on a Debian-based system.

### SPM

To install, include `'spm'` (case-insensitive) under `'software'` in the specifications dictionary. Valid keys within `'spm'` are keywords for [`neurodocker.interfaces.SPM`](neurodocker/interfaces/spm.py#L17). Currently, only SPM12 and MATLAB R2017a are supported.



## Example


In the following example, a dictionary of specifications is used to generate a Dockerfile. The resulting Docker image contains Python 3.5.1, Nipype, and ANTs 2.1.0.


```python
In [1]: from neurodocker.docker_api import Dockerfile, DockerImage, DockerContainer
      : from neurodocker.parser import SpecsParser

In [2]: specs = {
      :     'base': 'ubuntu:16.04',
      :     'conda_env': {
      :         'python_version': '3.5.1',
      :         'conda_install': ['traits'],
      :         'pip_install': ['https://github.com/nipy/nipype/archive/master.tar.gz']
      :     },
      :     'software': {
      :         'ants': {'version': '2.1.0', 'use_binaries': True},
      :     }
      : }

In [3]: parser = SpecsParser(specs=specs)
      : df = Dockerfile(parser.specs, pkg_manager='apt')

In [4]: from io import BytesIO
      : fileobj = BytesIO(df.cmd.encode('utf-8'))
      : image = DockerImage(fileobj=fileobj, tag="conda-ants").build()
      : image
Out[4]: <Image: 'conda-ants:latest'>

In [5]: container = DockerContainer(image)
      : container.start()

In [6]: container.exec_run('python -c "import nipype; print(nipype.__version__)"')
Out[6]: '0.13.0-dev\n'

In [7]: container.exec_run('ANTS')
Out[7]: ' call ANTS -h or ANTS --help \n'

In [8]: container.cleanup(remove=True, force=True)
```
