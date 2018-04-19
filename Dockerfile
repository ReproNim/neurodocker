FROM alpine:3.7

LABEL maintainer="Jakub Kaczmarzyk <jakubk@mit.edu>"

COPY . /opt/neurodocker

RUN tmp_pkgs="curl gcc musl-dev python3-dev sqlite-dev" \
    && apk add --update --no-cache git python3 rsync $tmp_pkgs \
    && curl -fsSL https://bootstrap.pypa.io/get-pip.py | python3 - \
    && pip install --no-cache-dir reprozip \
    && pip install --no-cache-dir -e /opt/neurodocker \
    && neurodocker --help \
    && apk del $tmp_pkgs

ENTRYPOINT ["neurodocker"]
