ARG PYTHON_VERSION=3.12
ARG PRIVATE_KEY=./default_server_key.pem

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /NPPS4
RUN mkdir data
VOLUME data
COPY ./alembic alembic
COPY ./beatmaps beatmaps
COPY ./npps4 npps4
COPY ./scripts scripts
COPY ./static static
COPY ./util util
COPY ./alembic.ini alembic.ini
COPY ./LICENSE.md LICENSE.md
COPY ./requirements.txt requirements.txt
COPY ${PRIVATE_KEY} default_server_key.pem

RUN python -m pip install -U pip
RUN pip install -r requirements.txt gunicorn uvicorn-worker asyncpg asyncmy

EXPOSE 51376/tcp
STOPSIGNAL SIGINT

ENTRYPOINT ["python", "scripts/bootstrap_docker.py"]
