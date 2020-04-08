FROM alpine:3.11.5

LABEL maintainer="Jakub Kaczmarzyk <jakubk@mit.edu>"

COPY . /opt/neurodocker

RUN apk add --update --no-cache git python3 \
    && rm -rf /var/cache/apk/* ~/.cache/pip/* \
    && python3 -m pip install --no-cache-dir -e /opt/neurodocker \
    && neurodocker --help

ENTRYPOINT ["neurodocker"]
