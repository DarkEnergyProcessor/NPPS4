ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-bookworm AS wheel_build

COPY requirements.txt requirements.txt
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install build-essential cmake
RUN pip wheel -r requirements.txt -w wheels gunicorn uvicorn-worker asyncpg asyncmy

FROM python:${PYTHON_VERSION}-slim-bookworm
COPY --from=wheel_build wheels wheels
WORKDIR /NPPS4
RUN mkdir data
VOLUME data
COPY ./alembic alembic
COPY ./beatmaps beatmaps
COPY ./external external
COPY ./npps4 npps4
COPY ./scripts scripts
COPY ./static static
COPY ./util util
COPY ./alembic.ini alembic.ini
COPY ./config.sample.toml config.sample.toml
COPY ./LICENSE.md LICENSE.md
COPY ./requirements.txt requirements.txt
ARG PRIVATE_KEY=default_server_key.pem
COPY ${PRIVATE_KEY} default_server_key.pem

RUN python -m pip install --root-user-action=ignore --no-cache-dir -U pip
RUN pip install --root-user-action=ignore --no-cache-dir --no-index --find-links=../wheels -r requirements.txt gunicorn uvicorn-worker asyncpg asyncmy
RUN rm -rf ../wheels

EXPOSE 51376/tcp

ENTRYPOINT ["python", "scripts/bootstrap_docker.py"]
