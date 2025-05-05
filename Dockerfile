# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /NPPS4
RUN mkdir data
VOLUME data

COPY ./alembic alembic
COPY ./beatmaps beatmaps
COPY ./external external
COPY ./npps4 npps4
COPY ./scripts scripts
COPY ./static static
COPY ./templates templates
COPY ./util util
COPY ./alembic.ini alembic.ini
COPY ./config.sample.toml config.sample.toml
COPY ./LICENSE.md LICENSE.md
COPY ./requirements.txt requirements.txt
COPY ./requirements-docker.txt requirements-docker.txt
ARG PRIVATE_KEY_FILE=default_server_key.pem
COPY ${PRIVATE_KEY_FILE} default_server_key.pem

RUN python -m pip install --root-user-action=ignore --no-cache-dir -U pip
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt -r requirements-docker.txt

EXPOSE 51376/tcp

ENTRYPOINT ["python", "scripts/bootstrap_docker.py"]
