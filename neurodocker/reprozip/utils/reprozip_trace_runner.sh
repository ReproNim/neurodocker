#!/usr/bin/env bash

# This script installs a dedicated Miniconda (not added to $PATH), installs
# ReproZip, runs `reprozip trace ...` on an arbitrary number of commands, and
# finally runs `reprozip pack`.
#
# This script accepts an arbitrary number of arguments, where each argument is
# a command to be traced. It is recommended to initialize an environment
# variable with the command string and to pass that environment variable to
# this script.

set -ex

REPROZIP_CONDA="/opt/reprozip-miniconda"
REPROZIP_TRACE_DIR="/neurodocker-reprozip-trace"
CONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
# This log prefix is used in trace.py.
NEURODOCKER_LOG_PREFIX="NEURODOCKER (in container)"


function program_exists() {
  hash "$1" 2>/dev/null;
}


function install_missing_dependencies() {
  if program_exists "apt-get"; then
    echo "${NEURODOCKER_LOG_PREFIX}: installing $1 with apt-get"
    apt-get update -qq
    apt-get install -yq $1
  elif program_exists "yum"; then
    echo "${NEURODOCKER_LOG_PREFIX}: installing $1 with yum"
    yum install -y -q $1
  else
    echo "${NEURODOCKER_LOG_PREFIX}: cannot install $1 (error using apt-get and then yum)."
    exit 1;
  fi;
}


function install_conda_reprozip() {
  TMP_CONDA_INSTALLER=/tmp/miniconda.sh
  ls /tmp
  curl -sSL -o "$TMP_CONDA_INSTALLER" "$CONDA_URL"
  ls /tmp
  bash $TMP_CONDA_INSTALLER -b -p $REPROZIP_CONDA
  rm -f $TMP_CONDA_INSTALLER
  ${REPROZIP_CONDA}/bin/conda install -yq --channel='conda-forge' python=3.6 reprozip
  ${REPROZIP_CONDA}/bin/conda install -yq sqlite
}


function run_reprozip_trace() {
  # https://askubuntu.com/a/674347
  cmds=("$@")
  reprozip_base_cmd="${REPROZIP_CONDA}/bin/reprozip trace -d ${REPROZIP_TRACE_DIR} --dont-identify-packages"

  for cmd in "${cmds[@]}";
  do
    # Only add --continue if it is not the first command.
    if [ "$cmd" == "${cmds[0]}" ]; then
        continue_=""
    else
        continue_="--continue"
    fi

    reprozip_cmd="${reprozip_base_cmd} ${continue_} ${cmd}"
    printf "${NEURODOCKER_LOG_PREFIX}: executing command:\t${reprozip_cmd}\n"
    {
      $reprozip_cmd
    } || {
      # Show relatively specific error message if a particular trace fails.
      printf "${NEURODOCKER_LOG_PREFIX}: ERROR: reprozip trace command exited with non-zero code. Command: $reprozip_cmd"
      exit 1
    }
  done
}


if [ ${#*} -eq 0 ]; then
  echo "${NEURODOCKER_LOG_PREFIX}: error: no arguments found."
  exit 1
fi

if [ -d $REPROZIP_TRACE_DIR ]; then
  echo "${NEURODOCKER_LOG_PREFIX}: WARN: overwriting reprozip trace directory: ${REPROZIP_TRACE_DIR}"
fi


if ! program_exists "bzip2" || ! program_exists "curl"; then
  install_missing_dependencies "bzip2 curl";
fi


if [ ! -f "${REPROZIP_CONDA}/bin/reprozip" ]; then
  echo "${NEURODOCKER_LOG_PREFIX}: installing dedicated Miniconda and ReproZip."
  install_conda_reprozip
else
  echo "${NEURODOCKER_LOG_PREFIX}: using installed reprozip."
fi

# Run reprozip trace.
echo "${NEURODOCKER_LOG_PREFIX}: running reprozip trace command(s)"
run_reprozip_trace "$@"

# Run reprozip pack.
REPROZIP_PATH_FILENAME=${REPROZIP_TRACE_DIR}/neurodocker-reprozip.rpz
echo "${NEURODOCKER_LOG_PREFIX}: packing up reprozip experiment"
${REPROZIP_CONDA}/bin/reprozip pack -d ${REPROZIP_TRACE_DIR} ${REPROZIP_PATH_FILENAME}
echo "${NEURODOCKER_LOG_PREFIX}: saved pack file within the container to"
echo "${REPROZIP_PATH_FILENAME}"
