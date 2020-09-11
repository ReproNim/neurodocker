#!/usr/bin/env bash

set -ex

which petpvc

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
