#!/usr/bin/env bash

set -ex

bet2 -h
flirt -version

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
