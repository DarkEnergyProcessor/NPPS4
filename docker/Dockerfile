ARG PYTHON_VERSION=3.12

FROM docker.io/library/python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /NPPS4/

COPY ./ /NPPS4/
COPY ./docker/start.sh /start.sh

ENTRYPOINT ["/start.sh"]
