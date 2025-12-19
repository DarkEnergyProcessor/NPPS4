# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim-trixie

WORKDIR /NPPS4
RUN mkdir data
VOLUME data

COPY ./requirements.txt requirements.txt
COPY ./requirements-perf.txt requirements-perf.txt
COPY ./requirements-docker.txt requirements-docker.txt
RUN python -m pip install --root-user-action=ignore --no-cache-dir -U pip
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt -r requirements-perf.txt -r requirements-docker.txt

# Least modified file first
ARG PRIVATE_KEY_FILE=default_server_key.pem
COPY ${PRIVATE_KEY_FILE} default_server_key.pem
COPY ./beatmaps beatmaps
COPY ./external external
COPY ./alembic.ini alembic.ini
COPY ./LICENSE.md LICENSE.md
COPY ./static static
COPY ./templates templates
COPY ./util util

COPY ./npps4 npps4
COPY ./scripts scripts
COPY ./main.py main.py
COPY ./config.sample.toml config.sample.toml

EXPOSE 51376/tcp

ENTRYPOINT ["python", "scripts/bootstrap_docker.py"]
