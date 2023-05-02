import json
import os

from .. import config

_NEED_GENERATION = (1, 1)

_archive_root: str = config.CONFIG_DATA["download"]["internal"]["archive_root"].replace("\\", "/")
if _archive_root[-1] == "/":
    _archive_root = _archive_root[:-1]


def get_server_version():
    return (0, 0)


def get_db_path(name: str) -> str:
    raise NotImplementedError("TODO")


def initialize():
    if not os.path.isdir(_archive_root):
        raise RuntimeError("The archive root directory is invalid")

    if os.path.isfile(_archive_root + "/generation.json"):
        with open(_archive_root + "/generation.json", "r", encoding="UTF-8", newline="") as f:
            generation: dict[str, int] = json.load(f)
    else:
        generation = {"major": 1, "minor": 0}

    if generation["major"] != _NEED_GENERATION[0] or _NEED_GENERATION[1] > generation["minor"]:
        raise RuntimeError("The specified archive directory structure is out-of-date")
