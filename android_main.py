# This script serve as main entrypoint for Chaquopy-based Android environment.
#
# The idiom is:
# setup_server()
# start_server() in another thread
# stop_server()

import asyncio
import os
import traceback
import urllib.parse

import uvicorn

import npps4.config.config

npps4.config.config._override_script_mode(False)

had_run_once = False


def _get_alembic_config():
    import alembic.config

    target_dir = npps4.config.config.BUNDLE_DIR or npps4.config.config.ROOT_DIR
    alembic_config = alembic.config.Config(os.path.join(target_dir, "alembic.ini"))
    script_location = alembic_config.get_alembic_option("script_location", "npps4/alembic")
    alembic_config.set_section_option("alembic", "script_location", os.path.join(target_dir, script_location))
    return alembic_config


def run_migrations():
    # Exception has to be made: Importing here reduces time needed for bootstrap script.
    import alembic.command

    alembic.command.upgrade(_get_alembic_config(), "head")


def run_data_migrations():
    import scripts.apply_fixes
    import npps4.evloop

    asyncio.run(scripts.apply_fixes.run_script([]), loop_factory=npps4.evloop.new_event_loop)


server_instance = None


def setup_server():
    global had_run_once

    had_run_once = True
    run_migrations()
    run_data_migrations()


def start_server(host: str = "127.0.0.1", port: int = 51376):
    global server_instance, had_run_once

    if server_instance is not None:
        raise RuntimeError("cannot start server twice")

    had_run_once = True
    import npps4.run.app

    cfg = uvicorn.Config(npps4.run.app.main, host=host, port=port, loop="npps4.evloop:new_event_loop")
    server_instance = uvicorn.Server(cfg)
    server_instance.run()
    server_instance = None


def stop_server():
    global server_instance

    si = server_instance
    if si is None or si.should_exit:
        raise RuntimeError("cannot stop server that's not started")

    si.should_exit = True


def import_database(db: bytes):
    if had_run_once:
        return 1  # ERROR_SERVER_ALREADY_RUN_ONCE

    if not db.startswith(b"SQLite format 3\0"):
        return 2  # ERROR_INVALID_SQLITE3

    parsed = urllib.parse.urlparse(npps4.config.config.get_database_url())
    if not (parsed.scheme == "sqlite" or parsed.scheme.startswith("sqlite+")):
        return 3  # ERROR_DATABASE_URL_NOT_SQLITE3

    dbpath = os.path.join(npps4.config.config.ROOT_DIR, parsed.path[1:])
    try:
        with open(dbpath, "wb") as f:
            f.write(db)

            try:
                os.remove(dbpath + "-shm")
            except FileNotFoundError:
                pass
            try:
                os.remove(dbpath + "-wal")
            except FileNotFoundError:
                pass

            return 0  # Ok
    except Exception as e:
        traceback.print_exception(e)
        return 4  # ERROR_UNKNOWN


def export_database():
    import sqlite3

    parsed = urllib.parse.urlparse(npps4.config.config.get_database_url())
    if not (parsed.scheme == "sqlite" or parsed.scheme.startswith("sqlite+")):
        return None

    dbpath = os.path.join(npps4.config.config.ROOT_DIR, parsed.path[1:])
    try:
        with sqlite3.connect(f"file:{urllib.parse.quote(dbpath)}?mode=ro", timeout=60, uri=True) as conn:
            return conn.serialize()
    except Exception as e:
        traceback.print_exception(e)
        return None


def nuke_database():
    if had_run_once:
        return 1  # ERROR_SERVER_ALREADY_RUN_ONCE

    parsed = urllib.parse.urlparse(npps4.config.config.get_database_url())
    if not (parsed.scheme == "sqlite" or parsed.scheme.startswith("sqlite+")):
        return 3  # ERROR_DATABASE_URL_NOT_SQLITE3

    dbpath = os.path.join(npps4.config.config.ROOT_DIR, parsed.path[1:])

    try:
        os.remove(dbpath)
    except FileNotFoundError:
        pass
    try:
        os.remove(dbpath + "-shm")
    except FileNotFoundError:
        pass
    try:
        os.remove(dbpath + "-wal")
    except FileNotFoundError:
        pass
