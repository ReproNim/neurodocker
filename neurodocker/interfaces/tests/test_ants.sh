#!/usr/bin/env bash

set -ex

Atropos --help
antsRegistration --version

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
