Null-Pointer Private Server: Revisited
=====

[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/Code%20style-black-000000.svg)](https://github.com/psf/black)

WIP SIF 9.11 private server written using FastAPI.

Notes
-----

* This project is currently in need of funding.

* Database schema changes constantly. Expect frequent database wipes.

Requirements
-----

Codes are tested on Python 3.12. Older Python version may work but no guarantees. To contribute, Python 3.12 is
required.

Install
----

1. Install Python 3.12 or later.
2. Create virtual environment.
3. Activate it.
4. `pip install -r requirements.txt`

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
file `main.server_private_key`.

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

```
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

Running
-----

After all is set, initialize the database:
```
alembic upgrade head
```

Then run the server
```
uvicorn npps4:uvicorn_main --port 51376
```

**Caveat**: Currently, `--workers` option is not supported when using NPPS4-DLAPI download backend.

Contribute
-----

See [CONTRIBUTE.md](CONTRIBUTE.md)


License
-----

zLib license, excluding any files in `external/`.

Public domain/unlicense, any files in `external/`.
