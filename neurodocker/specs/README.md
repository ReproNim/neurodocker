# Dockerfile instructions to install various software

Each software's entry requires instructions for at least one installation
method for at least one version or generic. Valid installation methods are
'binaries' and 'source'. The former installs pre-compiled binaries, and the
latter builds the software from source.

Generic installation instructions are instructions that apply to all versions. For example, the installation of all versions of ANTs consists of downloading and extracting the binaries. Because the installation method is consistent across versions, generic instructions can be used.


Tree structure of a program's entry.

```
<software>.yaml

generic || <version>
|-- binaries || source
|-- instructions
+-- dependencies
    +-- <package_manager>
        +-- <packages>
```

Requirements
------------
1. Installation instructions for at least one version or generic and at
   least one installation method, "binaries" or "source".
   - If instructions are supplied for a version or range of versions, generic
   instructions must be removed (they are no longer truly generic).
2. If the software has system-level dependencies, the package names must be
   listed for the `apt` and `yum` package managers.

Recommendations
---------------
1. Header with information about the software.

Version-specific instructions are available to accommodate variations in
installations across versions.


String formatting
-----------------
- `install_path`
- `install_deps`
- `binaries_url` : URL to binaries
- `source_url` : URL to source code
- `optional_*` : any optional keyword
