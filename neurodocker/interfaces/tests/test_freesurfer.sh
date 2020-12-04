#!/usr/bin/env bash

set -ex

# --help returns non-zero status code
mri_coreg --version
recon-all --version

printf 'passed'
echo
