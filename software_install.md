Installation instructions for neuroimaging software.


FSL
---

- [[install guide](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)]
- FSL recommends using their Python2 install script, which works on Centos but not on Ubuntu/Debian. The script installs the latest version of FSL. The `-f` argument can be used to specify a tarball to install (install older versions from FSL's [repository](https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions/)). Checksums are required (`-C`), but [those checksums](https://fsl.fmrib.ox.ac.uk/fsldownloads/md5sums/) seem to exist only for version 5.0.5+.
- To build from source on Ubuntu/Debian:
  - Assumes `build-essential` and `curl` are installed.
  - Install dependencies:
    - `apt-get update && apt-get install libexpat1-dev libx11-dev libgl1-mesa-dev zlib1g-dev`
  - Download source code: `curl -LO https://fsl.fmrib.ox.ac.uk/fsldownloads/oldversions/fsl-VERSION-sources.tar.gz`
  - Extract source: `tar zxf <tarball>`
  - Set `FSLDIR` environment variable: `export FSLDIR=$(pwd)/fsl`
  - In v5.0.6+, uncomment lines 52,53, and 55 in `${FSLDIR}/etc/fslconf/fsl.sh`
  - Set FSL environment variables: `. ${FSLDIR}/etc/fslconf/fsl.sh`
  - Check if machine is supported by default: `ls $FSLDIR/config/$FSLMACHTYPE`
    - If that command fails, copy the closest match: `cp -r $FSLDIR/config/closestmatch $FSLDIR/config/$FSLMACHTYPE`
  - symlink `install` and `ginstall`: `ln -s /usr/bin/install /usr/bin/ginstall`
  - `cd $FSLDIR` and run `./build`.
  - After following these steps, `precise-py27` docker container could not make `fslsurface`, `film`, `miscvis`, and `ptx2`.
- Update `PATH`:
  - `PATH=${FSLDIR}/bin:${PATH}`
  - `export FSLDIR PATH`



FreeSurfer
----------



AFNI
----
