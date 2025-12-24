import argparse
import glob
import os
import sys

from .config import config


def _get_alembic_config():
    import alembic.config

    target_dir = config.BUNDLE_DIR or config.ROOT_DIR
    alembic_config = alembic.config.Config(os.path.join(target_dir, "alembic.ini"))
    script_location = alembic_config.get_alembic_option("script_location", "npps4/alembic")
    alembic_config.set_section_option("alembic", "script_location", os.path.join(target_dir, script_location))
    return alembic_config


def run_command(host: str, port: int):
    # Exception has to be made: Importing here reduces time needed for bootstrap script.
    import alembic.command
    import uvicorn

    from .run import app

    alembic.command.upgrade(_get_alembic_config(), "head")
    uvicorn.run(app.main, host=host, port=port, loop="npps4.evloop:new_event_loop")


def script_command(script: str, args: list[str]):
    valid_scripts = {os.path.splitext(os.path.basename(v))[0]: v for v in glob.glob(config.ROOT_DIR + "/scripts/*.py")}
    # This is not a valid NPPS4 script per se
    if "bootstrap_docker" in valid_scripts:
        del valid_scripts["bootstrap_docker"]

    if script == "list":
        print("List of available scripts:")
        for k in valid_scripts.keys():
            print(f"* {k}")
        print()
    else:
        import asyncio
        import runpy

        from . import evloop

        module = runpy.run_path(valid_scripts[script])
        asyncio.run(module["run_script"](args), loop_factory=evloop.new_event_loop)


def main():
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Null-Pointer Private Server"
    )
    subparser = parser.add_subparsers(title="Command", dest="command")

    run_parser = subparser.add_parser(
        "run", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help="Run NPPS4 Server"
    )
    run_parser.add_argument(
        "-H", "--host", default=os.getenv("NPPS4_HOST", "0.0.0.0"), help="IP address for NPPS4 to listen on."
    )
    run_parser.add_argument(
        "-p", "--port", type=int, default=int(os.getenv("NPPS4_PORT", "51376")), help="TCP port for NPPS4 to listen on."
    )

    script_parser = subparser.add_parser(
        "script", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help="Run NPPS4 Script"
    )
    script_parser.add_argument("name", help="Script name, or 'list' to list all scripts.")

    if len(argv) == 0 or argv[0] not in {"run", "script", "-h", "--help"}:
        argv.insert(0, "run")

    args = parser.parse_args(argv)
    match args.command:
        case "run":
            run_command(args.host, args.port)
        case "script":
            script_command(args.name, argv[3:])


if __name__ == "__main__":
    main()
