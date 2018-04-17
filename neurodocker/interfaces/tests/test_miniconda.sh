#!/usr/bin/env bash

set -ex

if [ "$(python --version)" != "Python 3.5.1" ]; then
  echo "Python version incorrect."
  exit 1
fi

# Check that python packages were installed.
CONDA_LIST="$(conda list)"
for pkg in nipype pylsl traits; do
  PATTERN_MATCH=$(echo "$CONDA_LIST" | grep "^$pkg")
  if [ -z "$PATTERN_MATCH" ]; then
    echo "Python package not found: ${pkg}"
    exit 1
  fi
done
