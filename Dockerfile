FROM alpine:3.7

LABEL maintainer="Jakub Kaczmarzyk <jakubk@mit.edu>"

RUN tmp_pkgs="curl gcc musl-dev python3-dev sqlite-dev" \
    && apk add --update --no-cache git python3 py3-yaml rsync $tmp_pkgs \
    && curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3 - \
    && pip install --no-cache-dir reprozip \
    && apk del $tmp_pkgs \
    && rm -rf /var/cache/apk/* ~/.cache/pip/*

COPY . /opt/neurodocker
RUN pip install --no-cache-dir -e /opt/neurodocker \
    && neurodocker --help

ENTRYPOINT ["neurodocker"]
