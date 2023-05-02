Null-Pointer Private Server: Revisited
=====

WIP SIF 9.11 private server written using FastAPI.

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

NPPS4 provides default private key which is used to develop other private servers by the SIF community.
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

TODO: We'll provide game files when it's ready.

Database
-----

Please consult [SQLAlchemy supported database backends](https://docs.sqlalchemy.org/en/20/dialects/index.html) for more information.
If in doubt, SQLite3 is a safe choice if you don't need performance as it's already Python built-in as
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html) module.

Otherwise, install the additional dependencies depending on which backend you want to use.

Running
-----

After all is set, simply run:
```
uvicorn npps4:uvicorn_main --port 51376
```

**Caveat**: Currently, `--workers` option is not supported when using NPPS4-DLAPI download backend.

Contribute
-----

If you want to contribute, install [`black`](https://github.com/psf/black) and set it to format on save with maximum line length
of 120 characters (`-l 120`).

There are additional `import` rules for contributors:

* Never use `from ... import ...` both for Python standard library and 3rd-party library. Some might argue that this will
increase the line column length significantly but this makes it clear which module is used when reading the code.

* Only use `from ... import ...` for relative imports. Even in this case, it's not allowed to import function directly. Thus,
`from ... import some.func` is also not allowed under any circumstances. **Import the module directly!**
