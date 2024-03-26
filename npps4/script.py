import argparse
import asyncio

from . import script_dummy
from .config import config

from typing import Protocol


class Script(Protocol):
    async def run_script(self, args: list[str]): ...


def load_script(path: str):
    return config.load_module_from_file(path, "npps4_script_run")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=load_script, help="Script to run.")

    args, unk_args = parser.parse_known_args()
    script: Script = args.script
    await script.run_script(unk_args)


if __name__ == "__main__":
    asyncio.run(main())
