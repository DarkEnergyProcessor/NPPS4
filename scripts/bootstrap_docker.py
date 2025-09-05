#!/usr/bin/env python
# This script serve as entrypoint when NPPS4 runs under Docker.
# This is not regular NPPS4 script!

import os
import os.path
import shutil
import sys


def main() -> int:
    curdir = os.path.dirname(__file__)
    rootdir = os.path.normpath(os.path.join(curdir, ".."))
    datadir = os.path.join(rootdir, "data")
    worker_count = max(int(os.environ.get("NPPS4_WORKER", "1")), 1)
    python = sys.executable or "python"

    # Setup paths
    server_data = os.path.join(datadir, "server_data.json")
    if not os.path.exists(server_data):
        shutil.copy(os.path.join(rootdir, "npps4", "server_data.json"), server_data)

    external_script = os.path.join(datadir, "external")
    if not os.path.exists(external_script):
        shutil.copytree(os.path.join(rootdir, "external"), external_script, dirs_exist_ok=True)

    config_toml = os.path.join(datadir, "config.toml")
    if os.path.exists(config_toml):
        os.environ["NPPS4_CONFIG"] = config_toml

    print("Using config.toml path in container:", config_toml, flush=True)

    os.execlp(python, python, "main.py", "-w", str(worker_count))

    # In case os.exec* fails, this is executed
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
