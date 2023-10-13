import json
import os
import urllib.parse

import fastapi
import httpx
import pydantic

from . import dltype
from .. import config
from .. import idoltype
from .. import release_key
from .. import util

from typing import Any, Literal, TypeVar, overload


NEED_PROTOCOL_VERSION = (1, 1)


_public_info: dict[str, Any] = {}
_base_url: str = config.CONFIG_DATA["download"]["n4dlapi"]["server"]
_shared_key: str = config.CONFIG_DATA["download"]["n4dlapi"]["shared_key"]

if _base_url[-1] != "/":
    _base_url = _base_url + "/"


async def _call_api_async_notry(
    client: httpx.AsyncClient,
    endpoint: str,
    request_data: dict[str, Any] | list[Any] | None = None,
    /,
    *,
    raw: bool = False,
):
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

    response = await client.request(
        "GET" if request_data is None else "POST", parse.geturl(), headers=header, json=request_data
    )
    response.raise_for_status()
    if raw:
        return response.content
    else:
        return response.json()


@overload
async def _call_api_async(
    endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: Literal[False] = False
) -> Any:
    ...


@overload
async def _call_api_async(
    endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: Literal[True]
) -> bytes:
    ...


async def _call_api_async(
    endpoint: str, request_data: dict[str, Any] | list[Any] | None = None, /, *, raw: bool = False
):
    retry = 0
    async with httpx.AsyncClient() as client:
        while True:
            try:
                return await _call_api_async_notry(client, endpoint, request_data, raw=raw)
            except (json.JSONDecodeError, httpx.HTTPStatusError) as e:
                raise e from None
            except Exception as e:
                retry = retry + 1
                if retry >= 25:
                    raise e from None


def _call_api_notry(
    endpoint: str,
    request_data: dict[str, Any] | list[Any] | None = None,
    /,
    *,
    raw: bool = False,
):
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

    response = httpx.request(
        "GET" if request_data is None else "POST", parse.geturl(), headers=header, json=request_data
    )
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


_T = TypeVar("_T", bound=dltype.BaseInfo)


def _fixup_links(links: list[_T], platform: int):
    for link in links:
        if link.url.startswith("https://") and platform == 2:
            # Android doesn't support HTTPS
            link.url = "http" + link.url[5:]
    return links


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


UpdateInfoAdapter = pydantic.TypeAdapter(list[dltype.UpdateInfo])
BatchInfoAdapter = pydantic.TypeAdapter(list[dltype.BatchInfo])
BaseInfoAdapter = pydantic.TypeAdapter(list[dltype.BaseInfo])


async def get_update_files(
    request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
):
    result: list[dict[str, Any]] = await _call_api_async(
        "api/v1/update", {"version": util.sif_version_string(from_client_version), "platform": int(platform)}
    )
    return _fixup_links(UpdateInfoAdapter.validate_python(result), int(platform))


async def get_batch_files(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
):
    result: list[dict[str, Any]] = await _call_api_async(
        "api/v1/batch", {"package_type": package_type, "platform": int(platform), "exclude": exclude}
    )
    return _fixup_links(BatchInfoAdapter.validate_python(result), int(platform))


async def get_single_package(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
):
    try:
        result: list[dict[str, Any]] = await _call_api_async(
            "api/v1/download", {"package_type": package_type, "package_id": package_id, "platform": int(platform)}
        )
        return _fixup_links(BaseInfoAdapter.validate_python(result), int(platform))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise e from None


async def get_raw_files(request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]):
    result: list[dict[str, Any]] = await _call_api_async("api/v1/getfile", {"files": files, "platform": int(platform)})
    return _fixup_links(BaseInfoAdapter.validate_python(result), int(platform))


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
    release_key.update(_call_api("api/v1/release_info"))
