#!/usr/bin/env python
# This license applies to all source files in this directory and subdirectories.
#
# Copyright (c) 2024 Dark Energy Processor
#
# This software is provided 'as-is', without any express or implied warranty. In
# no event will the authors be held liable for any damages arising from the use of
# this software.
#
# Permission is granted to anyone to use this software for any purpose, including
# commercial applications, and to alter it and redistribute it freely, subject to
# the following restrictions:
#
# 1.  The origin of this software must not be misrepresented; you must not claim
#     that you wrote the original software. If you use this software in a product,
#     an acknowledgment in the product documentation would be appreciated but is
#     not required.
# 2.  Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
# 3.  This notice may not be removed or altered from any source distribution.
#
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
            "npps4.uvicorn_worker.Worker",
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
                "--loop",
                "npps4.evloop:new_event_loop",
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
                "--loop",
                "npps4.evloop:new_event_loop",
                "--port",
                str(args.port),
                "--host",
                str(args.host),
                "--workers",
                str(worker_count),
            )


if __name__ == "__main__":
    sys.exit(main())
