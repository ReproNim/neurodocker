#!/usr/bin/env bash

set -e
set -x

source activate default

# Check that python packages were installed.
CONDA_LIST="$(conda list)"
for pkg in nipype traits; do
  PATTERN_MATCH=$(echo "$CONDA_LIST" | grep "^$pkg")
  if [ -z "$PATTERN_MATCH" ]; then
    echo "Python package not found: ${pkg}"
    exit 1;
  fi
done
