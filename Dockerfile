# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

ARG PYTHON_VERSION=3.14
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-trixie-slim

WORKDIR /NPPS4
RUN mkdir data
VOLUME data

ENV PYTHONUNBUFFERED=1
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

COPY ./pyproject.toml ./pyproject.toml
COPY ./README.md README.md
COPY ./LICENSE.md LICENSE.md
COPY ./npps4 npps4
RUN uv sync --extra docker --extra dbsupp --extra desktop

# Least modified file first
ARG PRIVATE_KEY_FILE=default_server_key.pem
COPY ${PRIVATE_KEY_FILE} default_server_key.pem
COPY ./beatmaps beatmaps
COPY ./external external
COPY ./alembic.ini alembic.ini
COPY ./static static
COPY ./templates templates
COPY ./util util

COPY ./scripts scripts
COPY ./main.py main.py

EXPOSE 51376/tcp

ENTRYPOINT ["uv", "run", "scripts/bootstrap_docker.py"]
