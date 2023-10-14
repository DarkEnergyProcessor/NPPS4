Null-Pointer Private Server: Revisited
=====

WIP SIF 9.11 private server written using FastAPI.

Notes
-----

* This project is currently in need of funding.

* Database schema changes constantly. Expect frequent database wipes.

Requirements
-----

Codes are tested on Python 3.10, but should work on any later Python versions.

Install
----

1. Create virtual environment.
2. Activate it.
3. `pip install -r requirements.txt`

Starting Up
-----

Before starting the server, you need 2 things:
1. Get private key.
2. Get client game database.

### Get private key.

> **Warning**: A private key is required due to internal request-response verification done in the game. You must
have private key set-up!

#### Using provided private key

NPPS4 provides default private key which is used to develop other private servers by the community
and compatible with community-patched APK.

To use this private key, simply copy `default_server_key.pem` to `server_key.pem`.

To get the public key, run:

```
python make_server_key.py -p
```

#### Using your own private key

> **Warning**: The private key **must** be 1024-bit RSA stored in PEM format!

If you already have your existing private key, simply put them as `server_key.pem`.

#### Generating your own private key

To generate a new private key, run:

```
python make_server_key.py
```

The public key, for your game client will be printed to stdout in PEM format. Patch your game to use the
newly-provided public key.

### Get client game database.

Please look here for instruction on making your own archive-root directory: https://gist.github.com/MikuAuahDark/ece4eb73b3396403c6a2f11610a783b8

Database
-----

Please consult [SQLAlchemy supported database backends](https://docs.sqlalchemy.org/en/20/dialects/index.html) for
more information. If in doubt, SQLite3 is a safe choice if you don't need performance as it's already a part of NPPS4
required dependencies.

Otherwise, install the additional dependencies depending on which backend you want to use. Ensure to install the 
"async" version of the database packages!

Configuration
-----

Copy out `config.sample.toml` to `config.toml` and modify as needed.

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
