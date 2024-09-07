# When editing this, please synchronize the changes with config.sample.toml (and your own config.toml).
import re

import pydantic

from typing import Annotated

_VERSION_TEST = re.compile(r"^\d+\.\d+$")


def _test_version_string(v: str):
    if re.match(_VERSION_TEST, v) is None:
        raise ValueError('"client_version" must be in form of "major.minor".')
    return v


def _test_length(l: int):
    def inner(v: str):
        nonlocal l
        if len(v) != l:
            raise ValueError(f"the length must be {l}")
        return v

    return inner


class _Main(pydantic.BaseModel):
    data_directory: str = "data"
    secret_key: str
    server_private_key: str
    server_private_key_password: str = ""
    server_data: str
    session_expiry: int = 0


class _Database(pydantic.BaseModel):
    url: str


class _DownloadNone(pydantic.BaseModel):
    client_version: Annotated[str, pydantic.AfterValidator(_test_version_string)] = "59.4"


class _DownloadNPPS4DLAPI(pydantic.BaseModel):
    server: str
    shared_key: str = ""


class _DownloadInternal(pydantic.BaseModel):
    archive_root: str


class _DownloadCustom(pydantic.BaseModel):
    file: str


class _Download(pydantic.BaseModel):
    backend: str = "none"
    send_patched_server_info: bool = True
    none: _DownloadNone
    n4dlapi: _DownloadNPPS4DLAPI
    internal: _DownloadInternal
    custom: _DownloadCustom


class _Game(pydantic.BaseModel):
    badwords: str = "external/badwords.py"
    login_bonus: str = "external/login_bonus.py"
    beatmaps: str = "external/beatmap.py"
    live_unit_drop: str = "external/live_unit_drop.py"
    live_box_drop: str = "external/live_box_drop.py"


class _Advanced(pydantic.BaseModel):
    base_xorpad: Annotated[str, pydantic.AfterValidator(_test_length(32))] = "eit4Ahph4aiX4ohmephuobei6SooX9xo"
    application_key: Annotated[str, pydantic.AfterValidator(_test_length(32))] = "b6e6c940a93af2357ea3e0ace0b98afc"
    consumer_key: str = "lovelive_test"
    verify_xmc: bool = True


class _ImportExport(pydantic.BaseModel):
    enable_export: bool = False
    enable_import: bool = False
    bypass_signature: bool = False


class ConfigData(pydantic.BaseModel):
    main: _Main
    database: _Database
    download: _Download
    game: _Game
    advanced: _Advanced
    iex: _ImportExport = pydantic.Field(default_factory=_ImportExport)


__all__ = ["ConfigData"]
