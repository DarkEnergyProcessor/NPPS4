# NPPS4 agent guide

NPPS4 is a Python 3.12+ FastAPI server for the discontinued Love Live! School Idol Festival game.

## Where to work

- `npps4/game/`: game client endpoints, usually one module per feature; request/response models live in the endpoint module or `game/models.py`. `game/__init__.py` imports endpoint modules to register them.
- `npps4/system/`: reusable gameplay and account logic called by endpoints and `external/` scripts. Treat public functions here as compatibility contracts for those scripts.
- `npps4/idol/`: game request routing (`core.py`), request contexts and transaction lifecycle (`session.py`), database session access (`database.py`), and cache/error helpers.
- `npps4/db/`: SQLAlchemy tables; `main.py` defines server-owned data, while other modules map client game data. `npps4/alembic/` contains main database migrations.
- `npps4/data/schema.py`: structured server data models; `npps4/server_data.json` and `npps4/server_data_schema.json`: server data and its JSON schema. `npps4/config/` handles runtime configuration; `npps4/download/` selects and implements game file providers.
- `npps4/app/`: FastAPI app and routers; `npps4/run/`: launch entry points and router assembly. `npps4/webview/` serves game-facing HTML using root `templates/` and `static/`; `npps4/webui/` is the administrative UI with its own assets.
- `external/`: public-domain gameplay scripts; `beatmaps/`: game beatmaps; `npps4/serialcode/`: serial code handling; `npps4/scriptutils/` and root `scripts/`: script helpers and maintenance tools.

## Rules

- Follow `CONTRIBUTE.md`: format Python with Black at 120 columns. Group imports as standard library, third party, project-relative modules, then `typing`; sort each group. Use `import module` for standard library and third party packages, and import whole project modules with relative `from ... import module`. Type function parameters; use Python 3.12 generic syntax and `collections.abc` for collection protocols.
- Never commit or roll back a database transaction inside gameplay or system functions. The `BasicSchoolIdolContext` manager in `npps4/idol/session.py` owns commit, rollback, and cleanup; use `await context.db.main.flush()` when pending writes must reach the database before context exit.
- For main database schema changes, follow `CONTRIBUTE.md`: tell the human which tables/fields changed.
- Server setup and runtime requirements are in `README.md`; database breaking changes are tracked in `DBBREAKAGE.md`. Do not assume a local config, private key, or client game database exists.

## Workflow

- Agents may inspect files and write code. Due to sandbox constraints, the human might need to run most project commands manually, especially Black formatting and Alembic migrations. Give the exact commands needed and state which checks were not run; do not claim manual commands passed.
- The human writes and submits the PR. Do not create a PR or write its description; give the human a concise summary of code changes and any database schema changes instead.
