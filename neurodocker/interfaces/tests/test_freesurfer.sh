#!/usr/bin/env bash

set -ex

# --help returns non-zero status code
mri_coreg --version
recon-all --version

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
