Null-Pointer Private Server: Revisited
=====

[![Python: 3.14](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![Static Type Checker: Pyright](https://img.shields.io/badge/Static%20Type%20Checker-Pyright-CEB98F)](https://github.com/microsoft/pyright)
[![Code Style: black](https://img.shields.io/badge/Code%20Style-black-000000.svg)](https://github.com/psf/black)
[![Build](https://github.com/DarkEnergyProcessor/NPPS4/actions/workflows/main.yml/badge.svg)](https://github.com/DarkEnergyProcessor/NPPS4/actions/workflows/main.yml)

WIP SIF1 v9.11 private server written in Python 3.12+ using FastAPI.

Notes
-----

* This project is currently in need of funding.

* Database schema changes constantly. Expect frequent database wipes.

Requirements
-----

NPPS4 supports Python 3.12 and later. Python 3.14 is recommended.

Install Manually
----

1. Install Python 3.12 or later.
2. Create virtual environment.
3. Activate it.
4. Install all dependencies in `requirements-desktop.txt`.

Note: If you're using Termux (Unsupported), make sure to have Rust toolchain and use `requirements-android.txt` instead.

The command for normal Python is:
```sh
python -m venv .venv
source .venv/bin/activate # if using sh/bash
.venv\Scripts\activate # if using Command Prompt (NOT Powershell)
pip install -r requirements-desktop.txt # or requirememnts-android.txt for Termux
```

If using [`uv`](https://docs.astral.sh/uv/)
```sh
uv venv --python 3.14
uv pip install -r requirements-desktop.txt
```

Install with Docker
-----

If you want to build the container from source, run:
```sh
docker build -t npps4 .
```

Or, if you want to use pre-compiled container as part of NPPS4 CI, run:
```sh
docker pull ghcr.io/darkenergyprocessor/npps4:latest
```

Make a folder used for NPPS4 data directory (in this case, `path/to/data`), then copy `config.sample.toml` to
`path/to/data/config.toml`. Afterwards, configure `config.toml` as needed, mainly the download backend.

Then run the container:
```sh
docker run --name npps4 -v path/to/data:/NPPS4/data -p 0.0.0.0:51376:51376 -it npps4
```

Observe that the app is started successfully using:
```sh
docker logs npps4
```

> [!TIP]
> [WSLc](https://learn.microsoft.com/en-us/windows/wsl/wsl-container) might be supported, but untested. Feel free to
> fill bug report if it doesn't work there. Do note that WSLc doesn't support
> [`compose`](https://github.com/microsoft/WSL/issues/40948) yet.

Starting Up
-----

Before starting the server, you need 2 things:
1. Create configuration file.
2. Get client game database.
3. Get private key (optional).

### Create configuration file.

Copy out `config.sample.toml` to `config.toml` and adjust as needed. The file has extensive comments on each
configuration values.

### Get client game database.

There's 2 simple methods: Having local copy of SIF client files or loading it directly through internet.

#### Create local copy

First, follow the instruction at https://gist.github.com/MikuAuahDark/ece4eb73b3396403c6a2f11610a783b8.

Then set the `download.backend` to `internal` and configure the `download.internal.archive_root` directory in the
configuration file to your local copy of SIF client files.

#### Loading directly from internet

Look at the URL in https://gist.github.com/MikuAuahDark/ece4eb73b3396403c6a2f11610a783b8.

Set the `download.backend` to `n4dlapi` and configure `download.n4dlapi.server` to the URL writen in above gist (not
the gist itself).

### Get private key.

> [!TIP]
> This is an **optional and advanced stuff**. NPPS4 provides default private key (`default_server_key.pem`) which is
> used to develop other private servers by the community and compatible with community-patched APK. There's nothing to
> do to use this private key. **If in doubt, skip this!**

#### Using your own private key

> [!IMPORTANT]
> The private key **must** be 1024-bit RSA stored in PEM format!

If you already have your existing private key, simply put them as `server_key.pem`.

To get the public key, run:

```
python make_server_key.py -p
```

#### Generating your own private key

To generate a new private key, run:

```sh
python make_server_key.py
```

The public key, for your game client will be printed to stdout in PEM format. Patch your game to use the
newly-provided public key.

Database
-----

SQLite3 is a safe choice if you don't need performance as it's already a part of NPPS4 required dependencies. This is
suitable if you just play alone or with few friends. With the NPPS4 default configuration, the database will be stored
in `data/main.sqlite3`.

However, if you plan opening server for lots of people, SQLite3 won't suffice. You'd need something better like
PostgreSQL or MySQL. If installing manually, you need to install these additional dependencies:

* PostgreSQL: `psycopg` (**not** `psycopg2`)
* MySQL/MariaDB: `asyncmy`

> [!NOTE]
> Please consult [SQLAlchemy supported database backends](https://docs.sqlalchemy.org/en/21/dialects/) for more
> information.

If you're using the Docker images, only PostgreSQL (`psycopg`) is available. If you use/need other database support,
you need to derive the build image and install it. Consider using the provided example Docker Compose () for easier configuration.

Running
-----

### Quick and Easy

```sh
python -m npps4
uv run python -m npps4 # if using uv
```

### Using Uvicorn/Gunicorn

> [!NOTE]
> This method is useful if: you're developing NPPS4 and need script live reloading; or want to use multiple CPUs.

Initialize the database first:
```sh
python -m npps4 init
uv run python -m npps4 init # if using uv
```

Then run the server (add `--reload` for live reloading)
```sh
uvicorn npps4.run.app:main --port 51376 --host <your lan IP or 0.0.0.0> --loop npps4.evloop:new_event_loop
```

If you need to run with multiple workers, you must additionally install `gunicorn` and `uvicorn-worker` Python package.
```sh
pip install gunicorn uvicorn-worker # only needs to be done once

gunicorn --preload npps4.run.app:main -w 4 -k npps4.uvicorn_worker.UvicornWorker -b <your lan IP or 0.0.0.0>:51376
```

Updating
-----

Before updating, please ensure if database breakage is not happening. See [DBBREAKAGE.md](DBBREAKAGE.md) for
information.

If there's no database breakage or you already know a way to handle the breakage (either by doing stuff manually or
destroying the database), run:

```sh
git pull --ff-only
python -m npps4 init
uv run python -m npps4 init # if using uv
```

Most changes requires a server restart. However, changes that only touch `server_data.json` does not require server
restart as that particular file is hot-reloaded by the server.

Client App
-----

To get compatible client, please look at https://ethanthesleepy.one/. Both iOS and Android are supported.

Contribute
-----

See [CONTRIBUTE.md](CONTRIBUTE.md)


License
-----

zLib license, excluding any files in `external/`.

Public domain/unlicense, any files in `external/`.
