# When editing this, please synchronize the changes with config.sample.toml (and your own config.toml).
import os
import re

import pydantic
import pydantic_settings

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
    data_directory: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("data_directory", "datadir"))
    ] = "data"
    secret_key: Annotated[str, pydantic.Field(validation_alias=pydantic.AliasChoices("secret_key", "secretkey"))] = (
        "Hello World"
    )
    server_private_key: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("server_private_key", "pkey"))
    ] = "default_server_key.pem"
    server_private_key_password: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("server_private_key_password", "pkeypass"))
    ] = ""
    server_data: Annotated[str, pydantic.Field(validation_alias=pydantic.AliasChoices("server_data", "serverdata"))] = (
        "npps4/server_data.json"
    )
    session_expiry: Annotated[
        int, pydantic.Field(validation_alias=pydantic.AliasChoices("session_expiry", "tokenexpiry"))
    ] = 259200
    save_notes_list: Annotated[
        int, pydantic.Field(validation_alias=pydantic.AliasChoices("save_notes_list", "savenoteslist"))
    ] = False


class _Database(pydantic.BaseModel):
    url: str = "sqlite+aiosqlite:///data/main.sqlite3"


class _DownloadNone(pydantic.BaseModel):
    client_version: Annotated[
        str,
        pydantic.Field(validation_alias=pydantic.AliasChoices("client_version", "version")),
        pydantic.AfterValidator(_test_version_string),
    ] = "59.4"


class _DownloadNPPS4DLAPI(pydantic.BaseModel):
    server: str = ""
    shared_key: Annotated[str, pydantic.Field(validation_alias=pydantic.AliasChoices("shared_key", "key"))] = ""


class _DownloadInternal(pydantic.BaseModel):
    archive_root: Annotated[str, pydantic.Field(validation_alias=pydantic.AliasChoices("archive_root", "root"))] = ""


class _DownloadCustom(pydantic.BaseModel):
    file: str = ""


class _Download(pydantic.BaseModel):
    backend: str = ""
    send_patched_server_info: Annotated[
        bool, pydantic.Field(validation_alias=pydantic.AliasChoices("send_patched_server_info", "fixserverinfo"))
    ] = True
    none: _DownloadNone = pydantic.Field(default_factory=_DownloadNone)
    n4dlapi: _DownloadNPPS4DLAPI = pydantic.Field(default_factory=_DownloadNPPS4DLAPI)
    internal: _DownloadInternal = pydantic.Field(default_factory=_DownloadInternal)
    custom: _DownloadCustom = pydantic.Field(default_factory=_DownloadCustom)


class _Game(pydantic.BaseModel):
    badwords: str = "external/badwords.py"
    login_bonus: Annotated[str, pydantic.Field(validation_alias=pydantic.AliasChoices("login_bonus", "loginbonus"))] = (
        "external/login_bonus.py"
    )
    beatmaps: str = "external/beatmap.py"
    live_unit_drop: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("live_unit_drop", "unitdrop"))
    ] = "external/live_unit_drop.py"
    live_box_drop: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("live_box_drop", "boxdrop"))
    ] = "external/live_box_drop.py"


class _Advanced(pydantic.BaseModel):
    base_xorpad: Annotated[
        str,
        pydantic.Field(validation_alias=pydantic.AliasChoices("base_xorpad", "basekey")),
        pydantic.AfterValidator(_test_length(32)),
    ] = "eit4Ahph4aiX4ohmephuobei6SooX9xo"
    application_key: Annotated[
        str,
        pydantic.Field(validation_alias=pydantic.AliasChoices("application_key", "appkey")),
        pydantic.AfterValidator(_test_length(32)),
    ] = "b6e6c940a93af2357ea3e0ace0b98afc"
    consumer_key: Annotated[
        str, pydantic.Field(validation_alias=pydantic.AliasChoices("consumer_key", "consumerkey"))
    ] = "lovelive_test"
    verify_xmc: Annotated[bool, pydantic.Field(validation_alias=pydantic.AliasChoices("verify_xmc", "xmc"))] = True


class _ImportExport(pydantic.BaseModel):
    enable_export: Annotated[
        bool, pydantic.Field(validation_alias=pydantic.AliasChoices("enable_export", "export"))
    ] = False
    enable_import: Annotated[
        bool, pydantic.Field(validation_alias=pydantic.AliasChoices("enable_import", "import"))
    ] = False
    bypass_signature: Annotated[
        bool, pydantic.Field(validation_alias=pydantic.AliasChoices("bypass_signature", "bypass"))
    ] = False


class _Gameplay(pydantic.BaseModel):
    energy_multiplier: Annotated[
        float, pydantic.Field(validation_alias=pydantic.AliasChoices("energy_multiplier", "lpmul"))
    ] = 1
    love_multiplier: Annotated[
        float, pydantic.Field(validation_alias=pydantic.AliasChoices("love_multiplier", "lovemul"))
    ] = 1
    secretbox_cost_multiplier: Annotated[
        float, pydantic.Field(validation_alias=pydantic.AliasChoices("secretbox_cost_multiplier", "gachacostmul"))
    ] = 1


class ConfigData(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="NPPS4_CONFIG_",
        env_nested_delimiter="_",
        toml_file=os.environ.get("NPPS4_CONFIG", "config.toml"),
        nested_model_default_partial_update=True,
    )

    main: _Main = pydantic.Field(default_factory=_Main)
    database: _Database = pydantic.Field(default_factory=_Database)
    download: _Download = pydantic.Field(default_factory=_Download)
    game: _Game = pydantic.Field(default_factory=_Game)
    gameplay: _Gameplay = pydantic.Field(default_factory=_Gameplay)
    advanced: _Advanced = pydantic.Field(default_factory=_Advanced)
    iex: _ImportExport = pydantic.Field(default_factory=_ImportExport)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,
        env_settings: pydantic_settings.PydanticBaseSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:
        return env_settings, dotenv_settings, pydantic_settings.TomlConfigSettingsSource(settings_cls)

    @pydantic.model_validator(mode="after")
    def check_download_mode_sane(self):
        dl = self.download
        match dl.backend:
            case None:
                raise ValueError("NPPS4 download backend is not specified")
            case "none":
                pass
            case "n4dlapi":
                if not dl.n4dlapi.server:
                    raise ValueError("NPPS4 DLAPI missing server")
            case "internal":
                if not dl.internal.archive_root:
                    raise ValueError("Missing archive-root directory")
            case "custom":
                if not dl.custom.file:
                    raise ValueError("Missing Python script for custom downloader")

        return self


__all__ = ["ConfigData"]
