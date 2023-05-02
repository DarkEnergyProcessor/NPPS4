import json
import multiprocessing
import multiprocessing.managers
import os
import urllib.parse

import httpx
import pydantic

from . import dltype
from .. import config
from .. import idol
from .. import util

from typing import Any, Literal, overload


NEED_PROTOCOL_VERSION = (1, 1)


_public_info: dict[str, Any] = {}
_base_url: str = config.CONFIG_DATA["download"]["n4dlapi"]["server"]
_shared_key: str = config.CONFIG_DATA["download"]["n4dlapi"]["shared_key"]
_release_keys: dict[int, str] = {}

if _base_url[-1] != "/":
    _base_url = _base_url + "/"


def _call_api_notry(endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: bool = False):
    global _base_url
    parse_api = urllib.parse.urlparse(_base_url)
    parse = parse_api._replace(
        path=(parse_api.path if parse_api.path[-1] == "/" else parse_api.path[:-1])
        + (endpoint[1:] if endpoint[0] == "/" else endpoint)
    )

    header: dict[str, str] = {}
    if _shared_key:
        header["DLAPI-Shared-Key"] = urllib.parse.quote(_shared_key)
    if request_data is not None:
        header["Content-Type"] = "application/json"

    response = httpx.request("GET" if request_data is None else "POST", parse.geturl(), headers=header)
    response.raise_for_status()
    if raw:
        return response.content
    else:
        return response.json()


@overload
def _call_api(
    endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: Literal[False] = False
) -> Any:
    ...


@overload
def _call_api(endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: Literal[True]) -> bytes:
    ...


def _call_api(endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: bool = False):
    retry = 0
    while True:
        try:
            return _call_api_notry(endpoint, request_data, raw=raw)
        except (json.JSONDecodeError, httpx.HTTPStatusError) as e:
            raise e from None
        except Exception as e:
            retry = retry + 1
            if retry >= 25:
                raise e from None


def get_server_version():
    global _public_info
    if _public_info is None:
        raise RuntimeError("Forgot to initialize npps4 dlapi backend")
    return util.parse_sif_version(_public_info["gameVersion"])


def get_db_path(name: str):
    datadir = config.get_data_directory()
    ver = util.sif_version_string(get_server_version())

    # Get database
    target_db = f"{datadir}/db/{ver}/{name}.db_"
    if not os.path.isfile(target_db):
        # Download database
        print("Downloading database:", name)
        db_data = _call_api(f"api/v1/getdb/{name}", raw=True)
        os.makedirs(os.path.dirname(target_db), exist_ok=True)
        with open(target_db, "wb") as f:
            f.write(db_data)

    return target_db


def get_update_files(context: idol.SchoolIdolParams, platform: idol.PlatformType, from_client_version: tuple[int, int]):
    result: list[dict[str, Any]] = _call_api(
        "api/v1/update", {"version": util.sif_version_string(from_client_version), "platform": int(platform)}
    )
    return pydantic.parse_obj_as(list[dltype.UpdateInfo], result)


def get_batch_files(context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, exclude: list[int]):
    result: list[dict[str, Any]] = _call_api(
        "api/v1/batch", {"package_type": package_type, "platform": int(platform), "exclude": exclude}
    )
    return pydantic.parse_obj_as(list[dltype.BatchInfo], result)


def get_single_package(context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, package_id: int):
    result: list[dict[str, Any]] = _call_api(
        "api/v1/download", {"package_type": package_type, "package_id": package_id, "platform": int(platform)}
    )
    return pydantic.parse_obj_as(list[dltype.BaseInfo], result)


def get_raw_files(context: idol.SchoolIdolParams, platform: idol.PlatformType, files: list[str]):
    result: list[dict[str, Any]] = _call_api("api/v1/getfile", {"files": files, "platform": int(platform)})
    return pydantic.parse_obj_as(list[dltype.BaseInfo], result)


def get_release_keys() -> dict[int, str]:
    global _release_keys
    return _release_keys


def initialize():
    global _public_info, _base_url
    print("Getting public info API from external server")
    _public_info = _call_api("api/publicinfo")

    if (
        _public_info["dlapiVersion"]["major"] != NEED_PROTOCOL_VERSION[0]
        or NEED_PROTOCOL_VERSION[1] > _public_info["dlapiVersion"]["minor"]
    ):
        raise RuntimeError(
            "The specified server does not implement NPPS4-DLAPI Protocol " + ("%d.%d" % NEED_PROTOCOL_VERSION)
        )

    print("Getting release info keys")
    _release_keys.update(_call_api("api/v1/release_info"))
