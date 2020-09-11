#!/usr/bin/env bash

set -ex

dcm2niix -h

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
