#!/usr/bin/env python
# This script serve as entrypoint to run NPPS4, both in normal and
# containerized environment (e.g. Docker).

import argparse
import os
import subprocess
import sys

CURDIR = os.path.dirname(__file__)


def runwaitwin32(cmd: str, *args: str):
    try:
        return subprocess.call([cmd, *args[1:]], cwd=CURDIR)
    except KeyboardInterrupt:
        return 0


def wrapexec(cmd: str, *args: str):
    os.chdir(CURDIR)
    os.execvp(cmd, args)
    # In case os.exec* fails, this is executed
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-H", "--host", help="Bind to this address.", default="0.0.0.0")
    parser.add_argument("-p", "--port", help="Bind to this port.", type=int, default=51376)
    parser.add_argument(
        "-w", "--workers", help="Amount of workers.", type=int, default=max(int(os.environ.get("NPPS4_WORKER", "1")), 1)
    )
    parser.add_argument("--no-migrations", help="Disable alembic migrations.", action="store_true")
    parser.add_argument("--no-fixes", help="Disable running fixes.", action="store_true")
    parser.add_argument("--python", help="Python executable.", default=sys.executable)
    parser.add_argument("--reload", help="Reload on file changes (forces using uvicorn)", action="store_true")
    args = parser.parse_args()

    python: str = args.python or "python"
    worker_count: int = args.workers

    if not args.no_migrations:
        if subprocess.call([python, "-m", "alembic", "upgrade", "head"], cwd=CURDIR) != 0:
            print("alembic returned non-zero status code.")
            return 1

    if not args.no_fixes:
        if subprocess.call([python, "-m", "npps4.script", "scripts/apply_fixes.py"], cwd=CURDIR) != 0:
            print("NPPS4 fixes returned non-zero status code.")
            return 1

    executor = runwaitwin32 if os.name == "nt" else wrapexec

    if worker_count > 1 and os.name != "nt" and not args.reload:
        return executor(
            python,
            python,
            "-m",
            "gunicorn",
            "--preload",
            "npps4.run.app:main",
            "-w",
            str(worker_count),
            "-k",
            "uvicorn_worker.UvicornWorker",
            "-b",
            f"{args.host}:{args.port}",
        )
    else:
        if args.reload:
            return executor(
                python,
                python,
                "-m",
                "uvicorn",
                "npps4.run.app:main",
                "--port",
                str(args.port),
                "--host",
                str(args.host),
                "--workers",
                str(worker_count),
                "--reload",
            )
        else:
            return executor(
                python,
                python,
                "-m",
                "uvicorn",
                "npps4.run.app:main",
                "--port",
                str(args.port),
                "--host",
                str(args.host),
                "--workers",
                str(worker_count),
            )


if __name__ == "__main__":
    sys.exit(main())
