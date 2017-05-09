FROM alpine:3.5

LABEL maintainer="Jakub Kaczmarzyk <jakubk@mit.edu>"

COPY . /opt/neurodocker

RUN apk update -q \
    && apk add --no-cache python3 \
    && pip3 install --upgrade --no-cache-dir pip \
    && pip3 install --no-cache-dir /opt/neurodocker

ENTRYPOINT ["neurodocker"]
