#!/usr/bin/env bash
#
# Build all possible

set -ex

_base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
_generate_prefix="docker run --rm kaczmarj/neurodocker:test generate"
generate_docker="${_generate_prefix} docker"
generate_singularity="${_generate_prefix} singularity"

cache="${HOME}/neurodocker-tests/"$(date +"%Y-%m-%d_%H-%M-%S")""
mkdir -p "$cache"


function build_docker() {
  if [ -z "$1" ]; then
    echo "must provide path to Dockerfile"
    exit 10
  fi
  image_name="$(basename "$1")"
  docker build --tag="${image_name}" - < "$1"
}


function build_singularity() {
  if [ -z "$1" ]; then
    echo "must provide path to Singularity recipe"
    exit 11
  fi
  image_name="${cache}/$(basename "$1").simg"
  singularity build "${image_name}" "$1"
}

export -f build_docker
export -f build_singularity


if [ "${CIRCLE_NODE_TOTAL:-}" != "2" ]; then
  echo "These tests were designed to be run at 4x parallelism."
  exit 1
fi

${_base}/_generate_dockerfiles.py "$cache"

case ${CIRCLE_NODE_INDEX} in
  0)
    find "$cache" -name '*.docker' \
      | xargs -n1 -I {} bash -c "build_docker "$@"" _ {}
    exitcode=$?
    ;;
  1)
    find "$cache" -name '*.singularity' \
      | xargs -n1 -I {} bash -c "build_singularity "$@"" _ {}
    exitcode=$?
    ;;
esac

if [ "$exitcode" != "0" ]; then exit 1; fi
