#!/bin/bash

docker run --rm kaczmarj/neurodocker:master generate -b neurodebian:stretch-non-free -p apt \
--install fsl vim emacs-nox \
--add-to-entrypoint "source /etc/fsl/fsl.sh" \
--user=neuro \
--workdir /home/neuro \
--no-check-urls > Dockerfile