Null-Pointer Private Server: Revisited
=====

[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Static Type Checker: PyRight](https://img.shields.io/badge/Static%20Type%20Checker-PyRight-CEB98F)](https://github.com/microsoft/pyright)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)
[![Syntax Check](https://github.com/DarkEnergyProcessor/NPPS4/actions/workflows/syntax-check.yml/badge.svg)](https://github.com/DarkEnergyProcessor/NPPS4/actions/workflows/syntax-check.yml)

WIP SIF 9.11 private server written in Python 3.12 using FastAPI.

Notes
-----

* This project is currently in need of funding.

* Database schema changes constantly. Expect frequent database wipes.

Requirements
-----

NPPS4 currently supports only Python 3.12 (and possibly later version). Python 3.11 and earlier is not supported.

Install Manually
----

1. Install Python 3.12 or later.
2. Create virtual environment.
3. Activate it.
4. `pip install -r requirements.txt`

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

Then run the container for the first time so it setup the necessary data in `path/to/data`:

```sh
docker run --name npps4 -v path/to/data:/NPPS4/data -p 0.0.0.0:51376:51376 -it npps4
```

Configure `config.sample.toml` then **save it as `config.toml`** (or save the modified `config.sample.toml` first then
rename it). Now re-run the container:
```sh
docker start npps4
```

Observe that the app is started successfully using:
```sh
docker logs npps4
```

Starting Up
-----

Before starting the server, you need 3 things:
1. Create configuration file.
2. Get private key.
3. Get client game database.

### Create configuration file.

Copy out `config.sample.toml` to `config.toml` and adjust as needed. The file has extensive comments on each
configuration values.

### Get private key.

> [!WARNING]
> A private key is required due to internal request-response verification done in the game.

#### Using provided private key

NPPS4 provides default private key which is used to develop other private servers by the community
and compatible with community-patched APK.

There's nothing to do to use this private key. This private key is used by default as per the sample configuration
key `main.server_private_key`.

The public key of the default server key is:
```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDE0RNd6047aeBirzVb61DolatY
YWpaEUIPugOIkobHDc9qVR5iliMLyC0ErXO1siLBwN+U3zaDVOa5uhXbiS7uYq5c
cpxComxTnZtcn/b+mKDpYWLaC0Gv7UoiT8rpNqN3Vko645usz9OFc4VciijsHGRP
XmmmoP6qykfI/vba8wIDAQAB
-----END PUBLIC KEY-----
```

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

Database
-----

Please consult [SQLAlchemy supported database backends](https://docs.sqlalchemy.org/en/20/dialects/index.html) for
more information. If in doubt, SQLite3 is a safe choice if you don't need performance as it's already a part of NPPS4
required dependencies.

Otherwise, install the additional dependencies depending on which backend you want to use. Ensure to install the 
"async" version of the database packages!

* SQLite3: `aiosqlite` (already installed)
* PostgreSQL: `asyncpg`
* MySQL/MariaDB: `asyncmy`

Running
-----

After all is set, initialize the database:
```sh
alembic upgrade head
```

Then run the server
```sh
uvicorn npps4.run.app:main --port 51376 --host <your lan IP or 0.0.0.0>
```

If you need to run with multiple workers, you must additionally install `gunicorn` and `uvicorn-worker` Python package.
```sh
pip install gunicorn uvicorn-worker # only needs to be done once

gunicorn --preload npps4.run.app:main -w 4 -k uvicorn_worker.UvicornWorker -b <your lan IP or 0.0.0.0>:51376
```

Updating
-----

Before updating, please ensure if database breakage is not happening. See [DBBREAKAGE.md](DBBREAKAGE.md) for
information.

If there's no database breakage or you already know a way to handle the breakage (either by doing stuff manually or
destroying the database), run:

```
git pull --ff-only
alembic upgrade head
```

Most changes requires a server restart. However, changes that only touch `server_data.json` does not require server
restart as that particular file is hot-reloaded by the server.

Client App
-----

To get compatible client, please look at https://ethanaobrien.github.io/sif-patcher/. Both iOS and Android are
supported.

Contribute
-----

See [CONTRIBUTE.md](CONTRIBUTE.md)


License
-----

zLib license, excluding any files in `external/`.

Public domain/unlicense, any files in `external/`.
