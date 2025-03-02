FROM python:3.9-alpine

COPY . /opt/neurodocker

RUN apk add --update --no-cache git \
    && python -m pip install --no-cache-dir --editable /opt/neurodocker \
    && neurodocker --help

LABEL maintainer="Jakub Kaczmarzyk <jakub.kaczmarzyk@gmail.com>"

ENTRYPOINT ["neurodocker"]
