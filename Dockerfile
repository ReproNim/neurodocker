FROM alpine:3.11.5

COPY . /opt/neurodocker

RUN apk add --update --no-cache git python3 \
    && python3 -m pip install --no-cache-dir --editable /opt/neurodocker \
    && neurodocker --help

LABEL maintainer="Jakub Kaczmarzyk <jakub.kaczmarzyk@gmail.com>"

ENTRYPOINT ["neurodocker"]
