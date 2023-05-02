import json
import os

from . import dltype
from .. import config
from .. import idol

_NEED_GENERATION = (1, 1)

_archive_root: str = config.CONFIG_DATA["download"]["internal"]["archive_root"].replace("\\", "/")
if _archive_root[-1] == "/":
    _archive_root = _archive_root[:-1]


def get_server_version():
    return (0, 0)


def get_db_path(name: str) -> str:
    raise NotImplementedError("TODO")


def get_update_files(
    context: idol.SchoolIdolParams, platform: idol.PlatformType, from_client_version: tuple[int, int]
) -> list[dltype.UpdateInfo]:
    raise NotImplementedError("not implemented get_update_files")


def get_batch_files(
    context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, exclude: list[int]
) -> list[dltype.BatchInfo]:
    raise NotImplementedError("not implemented get_batch_files")


def get_single_package(
    context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, package_id: int
) -> list[dltype.BaseInfo]:
    raise NotImplementedError("not implemented get_single_package")


def get_release_keys() -> dict[int, str]:
    return {}


def get_raw_files(context: idol.SchoolIdolParams, platform: idol.PlatformType, files: list[str]):
    target = str(context.request.url)
    target = (target + "missing") if target[-1] == "/" else (target + "/missing")
    return [
        dltype.BaseInfo(
            url=target,
            size=0,
            checksums=dltype.Checksum(
                md5="d41d8cd98f00b204e9800998ecf8427e",
                sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ),
        )
    ] * len(files)


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
