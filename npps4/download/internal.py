import json
import os

import fastapi
import fastapi.staticfiles

from . import dltype
from .. import idoltype
from .. import release_key
from .. import util
from ..app import app
from ..config import config

from typing import Callable, Any

_NEED_GENERATION = (1, 1)
_PLATFORM_MAP = ["iOS", "Android"]

_archive_root: str = config.CONFIG_DATA.download.internal.archive_root.replace("\\", "/")
if _archive_root[-1] == "/":
    _archive_root = _archive_root[:-1]


class _MemoizeByModTime[_T]:
    def __init__(self, f: Callable[[str], _T]):
        self.f = f
        self.map: dict[str, tuple[int, _T]] = {}

    def __call__(self, path: str):
        stat = os.stat(path)
        if path in self.map:
            mtime, result = self.map[path]
            if stat.st_mtime_ns <= mtime:
                return result
        result = self.f(path)
        self.map[path] = (stat.st_mtime_ns, result)
        return result


@_MemoizeByModTime
def _read_json(file: str):
    with open(file, "r", encoding="UTF-8", newline="") as f:
        return json.load(f)


@_MemoizeByModTime
def _get_versions(file: str):
    versions: list[str] = _read_json(file)
    new_ver: list[tuple[int, int]] = []
    for ver in versions:
        try:
            new_ver.append(util.parse_sif_version(ver))
        except ValueError:
            pass
    new_ver.sort()
    return new_ver


def get_server_version():
    for oses in _PLATFORM_MAP:
        target = f"{_archive_root}/{oses}/package/info.json"
        if os.path.isfile(target):
            return _get_versions(target)[-1]

    raise RuntimeError("No package found!")


def get_db_path(name: str) -> str:
    global _update_preference
    latest = get_server_version()
    for oses in _PLATFORM_MAP:
        path = f"{_archive_root}/{oses}/package/{util.sif_version_string(latest)}/db/{name}.db_"
        if os.path.isfile(path):
            return path

    raise RuntimeError(f"Database '{name}' not found")


async def get_update_files(
    request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
) -> list[dltype.UpdateInfo]:
    path = f"{_archive_root}/{_PLATFORM_MAP[platform - 1]}/update"
    updates = _get_versions(path + "/infov2.json")
    if from_client_version == updates[-1]:
        # Up-to-date
        return []

    # Get download files
    download_data: list[dltype.UpdateInfo] = []
    for ver in filter(lambda x: x > from_client_version, updates):
        verstr = util.sif_version_string(ver)
        update_ver_path = f"{path}/{verstr}"
        file_datas: list[dict[str, Any]] = _read_json(update_ver_path + "/infov2.json")
        for filedata in file_datas:
            download_data.append(
                dltype.UpdateInfo(
                    url=str(
                        request.url_for(
                            "archive_root", path=f"{_PLATFORM_MAP[platform - 1]}/update/{verstr}/{filedata['name']}"
                        )
                    ),
                    size=filedata["size"],
                    checksums=dltype.Checksum(md5=filedata["md5"], sha256=filedata["sha256"]),
                    version=verstr,
                )
            )

    return download_data


async def get_batch_files(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
) -> list[dltype.BatchInfo]:
    latest = get_server_version()
    latest_verstr = util.sif_version_string(latest)
    path = f"{_archive_root}/{_PLATFORM_MAP[platform - 1]}/package/{latest_verstr}/{package_type}"
    result: list[dltype.BatchInfo] = []
    packages: list[int] = _read_json(path + "/info.json")

    for pkgid in sorted(set(packages).difference(exclude)):
        file_datas: list[dict[str, Any]] = _read_json(f"{path}/{pkgid}/infov2.json")
        for filedata in file_datas:
            result.append(
                dltype.BatchInfo(
                    url=str(
                        request.url_for(
                            "archive_root",
                            path=f"{_PLATFORM_MAP[platform - 1]}/package/{latest_verstr}/{package_type}/{pkgid}/{filedata['name']}",
                        )
                    ),
                    size=filedata["size"],
                    checksums=dltype.Checksum(md5=filedata["md5"], sha256=filedata["sha256"]),
                    packageId=pkgid,
                )
            )

    return result


async def get_single_package(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
) -> list[dltype.BaseInfo] | None:
    latest = get_server_version()
    latest_verstr = util.sif_version_string(latest)
    path = f"{_archive_root}/{_PLATFORM_MAP[platform - 1]}/package/{latest_verstr}/{package_type}/{package_id}"
    if not os.path.isdir(path):
        return None

    result: list[dltype.BaseInfo] = []
    file_datas: list[dict[str, Any]] = _read_json(f"{path}/infov2.json")
    for filedata in file_datas:
        result.append(
            dltype.BaseInfo(
                url=str(
                    request.url_for(
                        "archive_root",
                        path=f"{_PLATFORM_MAP[platform - 1]}/package/{latest_verstr}/{package_type}/{package_id}/{filedata['name']}",
                    )
                ),
                size=filedata["size"],
                checksums=dltype.Checksum(md5=filedata["md5"], sha256=filedata["sha256"]),
            )
        )

    return result


async def get_raw_files(request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]):
    latest = get_server_version()
    # Normalize path
    commonpath = f"{_PLATFORM_MAP[platform - 1]}/package/{util.sif_version_string(latest)}/microdl"
    basepath = f"{_archive_root}/{commonpath}"
    microdl_map: dict[str, dict[str, Any]] = _read_json(basepath + "/info.json")
    result: list[dltype.BaseInfo] = []

    for file in files:
        sanitized_file = os.path.normpath(file.replace("..", "")).replace("\\", "/")
        if sanitized_file[0] == "/":
            sanitized_file = sanitized_file[1:]
        path = f"{commonpath}/{sanitized_file}"

        # Get microdl_map
        base_info = dltype.BaseInfo(
            url=str(request.url_for("archive_root", path=path)),
            size=0,
            checksums=dltype.Checksum(),
        )
        if sanitized_file in microdl_map:
            info = microdl_map[sanitized_file]
            base_info.size = info["size"]
            base_info.checksums.md5 = info["md5"]
            base_info.checksums.sha256 = info["sha256"]
        result.append(base_info)

    return result


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

    release_info: dict[str, str] = _read_json(f"{_archive_root}/release_info.json")
    release_key.update({int(k): v for k, v in release_info.items()})

    app.core.mount("/archive-root", fastapi.staticfiles.StaticFiles(directory=_archive_root), "archive_root")
