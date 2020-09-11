#!/usr/bin/env bash

set -ex

3dSkullStrip -help

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
