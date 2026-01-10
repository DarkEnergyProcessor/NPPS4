# This script serve as main entrypoint for Chaquopy-based Android environment.
#
# The idion is:
# setup_server()
# start_server() in another thread
# stop_server()

import asyncio
import os

import uvicorn

import npps4.config.config

npps4.config.config._override_script_mode(False)


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
    run_migrations()
    run_data_migrations()


def start_server():
    global server_instance

    if server_instance is not None:
        raise RuntimeError("cannot start server twice")

    import npps4.run.app

    cfg = uvicorn.Config(npps4.run.app.main, host="127.0.0.1", port=51376, loop="npps4.evloop:new_event_loop")
    server_instance = uvicorn.Server(cfg)
    server_instance.run()
    server_instance = None


def stop_server():
    global server_instance

    si = server_instance
    if si is None or si.should_exit:
        raise RuntimeError("cannot stop server that's not started")

    si.should_exit = True
