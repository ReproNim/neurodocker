#!/usr/bin/env bash

set -e
set -x

# --help returns non-zero status code (causes error in pytest).
mri_coreg --version
recon-all --version
