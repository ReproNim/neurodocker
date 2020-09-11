#!/usr/bin/env bash

set -e

c3d -h

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
