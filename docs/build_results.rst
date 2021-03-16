Build Results
=============

The table below lists the build results for the templates included in Neurodocker.
These builds are parameterized over many variables, including version, package manager,
base image, builder (Docker or Singularity), and installation method (binaries or
source).

| 🟢 = passed
| 🔴 = failed
| 🟡 = unknown

.. list-table:: Build results
   :header-rows: 1

   * - outcome
     - template
     - method
     - arguments
     - package manager
     - base image
     - builder
   * - 🟢
     - mrtrix3
     - binaries
     - | method="binaries"
       | version="3.0.0"
     - apt
     - debian:buster-slim
     - docker
   * - 🟢
     - mrtrix3
     - binaries
     - | method="binaries"
       | version="3.0.0"
     - yum
     - centos:7
     - docker
   * - 🟢
     - mrtrix3
     - binaries
     - | method="binaries"
       | version="3.0.0"
     - apt
     - debian:buster-slim
     - singularity
   * - 🟢
     - mrtrix3
     - binaries
     - | method="binaries"
       | version="3.0.0"
     - yum
     - centos:7
     - singularity
