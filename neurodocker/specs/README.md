Generic Dockerfile instructions to install various software.

Each program's entry requires instructions for at least one installation
method for at least one version or generic. Valid installation methods are
'binaries' and 'source'. The former installs pre-compiled binaries, and the
latter builds the software from source.

Requirements
------------
1. Installation instructions for at least one version or generic and at
   least one installation method, "binaries" or "source".
2. If the software has system-level dependencies, the package names must be
   listed for the `apt` and `yum` package managers.

Recommendations
---------------
1. Header with information about the software.

Version-specific instructions are available to accommodate variations in
installations across versions.

Tree structure of a program's entry.

```
<program>.yaml

generic || <version>
|-- binaries || source
|-- instructions
+-- dependencies
    |-- <package_manager>
    |   +-- <packages>
```
