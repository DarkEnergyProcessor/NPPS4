Null-Pointer Private Server: Revisited
=====

WIP SIF 9.10+ private server written using Flask.

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
1. Generate private key.
2. Get client game database.

### Generate private key.

```
python make_server_key.py
```

The public key, for your game client will be printed to stdout in PEM format.

### Get client game database.

NPPS needs the client game data. **In the future this should be provided once the game service ended.**

For time being, create new SIF account and put the account credentials as `credentials.json`:
```json
{
	"LOVELIVE_ID": "your login_key",
	"LOVELIVE_PW": "your login_passwd"
}
```

Then extract the game "install" assets (protip: `AppAssets.zip` in Android) to `data/install`. Afterwards:

```
python update_data.py
```

Database
-----

Please consult [SQLAlchemy supported database backends](https://docs.sqlalchemy.org/en/20/dialects/index.html) for more information.
If in doubt, SQLite3 is a safe choice if you don't need performance as it's already Python built-in as
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html) module.

Otherwise, install the additional dependencies depending on which backend you want to use.

Contribute
-----

If you want to contribute, install [`black`](https://github.com/psf/black) and set it to format on save with maximum line length
of 120 characters (`-l 120`).
