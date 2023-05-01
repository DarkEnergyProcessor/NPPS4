from . import none as none_backend
from . import n4dlapi as n4dlapi_backend
from . import internal as internal_backend

from .. import config

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


CURRENT_BACKEND.initialize()
