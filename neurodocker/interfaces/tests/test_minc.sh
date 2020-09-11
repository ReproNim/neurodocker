#!/usr/bin/env bash

set -ex

mincresample -version

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
