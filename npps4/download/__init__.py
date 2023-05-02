from . import none as none_backend
from . import n4dlapi as n4dlapi_backend
from . import internal as internal_backend

from . import dltype
from .. import config
from .. import idol

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
    def get_update_files(
        context: idol.SchoolIdolParams, platform: idol.PlatformType, from_client_version: tuple[int, int]
    ) -> list[dltype.UpdateInfo]:
        ...

    @staticmethod
    def get_batch_files(
        context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, exclude: list[int]
    ) -> list[dltype.BatchInfo]:
        ...

    @staticmethod
    def get_single_package(
        context: idol.SchoolIdolParams, platform: idol.PlatformType, package_type: int, package_id: int
    ) -> list[dltype.BaseInfo]:
        ...

    @staticmethod
    def get_raw_files(
        context: idol.SchoolIdolParams, platform: idol.PlatformType, files: list[str]
    ) -> list[dltype.BaseInfo]:
        ...

    @staticmethod
    def get_release_keys() -> dict[int, str]:
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


def get_formatted_release_keys():
    global CURRENT_BACKEND
    relkeys = CURRENT_BACKEND.get_release_keys()
    return [{"id": k, "key": v} for k, v in relkeys.items()]


CURRENT_BACKEND.initialize()
