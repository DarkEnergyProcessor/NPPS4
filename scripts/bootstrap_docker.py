#!/usr/bin/env python
# This script serve as entrypoint when NPPS4 runs under Docker.
# This is not regular NPPS4 script!

import os
import os.path
import shutil


def main() -> int:
    curdir = os.path.dirname(__file__)
    rootdir = os.path.normpath(os.path.join(curdir, ".."))
    datadir = os.path.join(rootdir, "data")
    worker_count = max(int(os.environ.get("NPPS4_WORKER", "1")), 1)

    # Setup paths
    server_data = os.path.join(datadir, "server_data.json")
    if not os.path.exists(server_data):
        shutil.copy(os.path.join(rootdir, "npps4", "server_data.json"), server_data)

    external_script = os.path.join(datadir, "external")
    if not os.path.exists(external_script):
        shutil.copytree(os.path.join(rootdir, "external"), external_script, dirs_exist_ok=True)

    config_toml = os.path.join(datadir, "config.toml")
    if not os.path.exists(config_toml):
        config_sample_toml = os.path.join(datadir, "config.sample.toml")
        has_sample = os.path.exists(config_sample_toml)

        if not has_sample:
            with open(os.path.join(rootdir, "config.sample.toml"), "r", encoding="utf-8", newline="") as f:
                config_content = f.read()

            config_content = config_content.replace(' = "external/', ' = "data/external/')
            config_content = config_content.replace(
                'server_data = "npps4/server_data.json"', 'server_data = "data/server_data.json"'
            )

            with open(config_sample_toml, "w", encoding="utf-8", newline="") as f:
                f.write(config_content)

            print(
                "Setup complete. What's next?\n1. Modify data/config.sample.toml as needed\n2. Rename config.sample.toml to config.toml\n3. Re-run the container."
            )
        else:
            print("Make sure data/config.toml is available!")

        return 1

    # Setup
    os.environ["NPPS4_CONFIG"] = config_toml
    print("Using config.toml path in container:", config_toml, flush=True)

    if os.system("alembic upgrade head") != 0:
        print("alembic returned non-zero status code.")
        return 1

    if worker_count > 1:
        os.execlp(
            "gunicorn",
            "gunicorn",
            "--preload",
            "npps4.run.app:main",
            "-w",
            str(worker_count),
            "-k",
            "uvicorn_worker.UvicornWorker",
            "-b",
            "0.0.0.0:51376",
        )
    else:
        os.execlp(
            "uvicorn",
            "uvicorn",
            "npps4.run.app:main",
            "--port",
            "51376",
            "--host",
            "0.0.0.0",
        )

    # In case os.exec* fails, this is executed
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
