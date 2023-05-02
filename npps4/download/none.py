import os

import fastapi

from . import dltype
from .. import config
from .. import util
from .. import idoltype


def get_server_version():
    return util.parse_sif_version(config.CONFIG_DATA["download"]["none"]["client_version"])


def get_db_path(name: str) -> str:
    path = f"{config.get_data_directory()}/db/{name}.db_"
    if os.path.isfile(path):
        return path

    raise NotImplementedError(f"'none' backend does not automatically load databases! Unable to find '{path}'")


def get_update_files(
    request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
) -> list[dltype.UpdateInfo]:
    raise NotImplementedError("not implemented get_update_files")


def get_batch_files(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
) -> list[dltype.BatchInfo]:
    raise NotImplementedError("not implemented get_batch_files")


def get_single_package(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
) -> list[dltype.BaseInfo] | None:
    return None


def get_release_keys() -> dict[int, str]:
    return {}


def get_raw_files(request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]):
    target = str(request.url)
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
    pass
