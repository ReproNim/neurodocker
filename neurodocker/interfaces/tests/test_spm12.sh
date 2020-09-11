#!/usr/bin/env bash

set -exu

echo "a = 1" > ~/test.m
$SPMMCRCMD ~/test.m

# Print to stderr because it is unbuffered.
>&2 printf 'passed'
