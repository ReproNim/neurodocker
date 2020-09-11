#!/usr/bin/env bash

set -ex

mrthreshold --help

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
