import fastapi

from . import none as none_backend
from . import n4dlapi as n4dlapi_backend
from . import internal as internal_backend

from . import dltype
from .. import config
from .. import idoltype

from typing import Protocol


class _DLBackend(Protocol):
    @staticmethod
    def initialize():
        ...

    @staticmethod
    def get_server_version() -> tuple[int, int]:
        ...

    @staticmethod
    def get_db_path(name: str) -> str:
        ...

    @staticmethod
    async def get_update_files(
        request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
    ) -> list[dltype.UpdateInfo]:
        ...

    @staticmethod
    async def get_batch_files(
        request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
    ) -> list[dltype.BatchInfo]:
        ...

    @staticmethod
    async def get_single_package(
        request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
    ) -> list[dltype.BaseInfo] | None:
        ...

    @staticmethod
    async def get_raw_files(
        request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]
    ) -> list[dltype.BaseInfo]:
        ...


BACKENDS: dict[str, _DLBackend] = {"none": none_backend, "n4dlapi": n4dlapi_backend, "internal": internal_backend}

if config.CONFIG_DATA["download"]["backend"] not in BACKENDS:
    raise RuntimeError(f"Missing or unknown backend '{config.CONFIG_DATA['download']['backend']}'")

CURRENT_BACKEND = BACKENDS[config.CONFIG_DATA["download"]["backend"]]


def get_server_version():
    global CURRENT_BACKEND
    return CURRENT_BACKEND.get_server_version()


def get_db_path(name: str):
    global CURRENT_BACKEND
    return CURRENT_BACKEND.get_db_path(name)


async def get_update_files(
    request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
):
    global CURRENT_BACKEND
    return await CURRENT_BACKEND.get_update_files(request, platform, from_client_version)


async def get_batch_files(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
):
    global CURRENT_BACKEND
    return await CURRENT_BACKEND.get_batch_files(request, platform, package_type, exclude)


async def get_single_package(
    request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
):
    global CURRENT_BACKEND
    return await CURRENT_BACKEND.get_single_package(request, platform, package_type, package_id)


async def get_raw_files(request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]):
    global CURRENT_BACKEND
    return await CURRENT_BACKEND.get_raw_files(request, platform, files)


CURRENT_BACKEND.initialize()
