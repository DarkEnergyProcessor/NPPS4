import importlib
import importlib.machinery
import importlib.util
import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import Cryptodome.PublicKey.RSA

from . import cfgtype, data

from typing import cast

ROOT_DIR = os.path.normpath(os.path.dirname(__file__) + "/../..")
os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)


try:
    with open(os.path.normpath(os.path.join(ROOT_DIR, "config.toml")), "rb") as f:
        CONFIG_DATA = data.ConfigData.model_validate(tomllib.load(f), strict=True)
except IOError as e:
    raise Exception("Unable to load config.toml. Is it present in the project root?") from e

try:
    with open(os.path.join(ROOT_DIR, CONFIG_DATA.main.server_private_key), "rb") as f:
        key_password = os.environ.get("NPPS_KEY_PASSWORD", CONFIG_DATA.main.server_private_key_password)
        if key_password == "":
            key_password = None

        _SERVER_KEY = Cryptodome.PublicKey.RSA.import_key(f.read(), key_password)
except IOError as e:
    raise Exception("Unable to load server private key. Double-check your configuration.") from e


def get_data_directory():
    global ROOT_DIR
    return os.path.abspath(os.path.join(ROOT_DIR, CONFIG_DATA.main.data_directory)).replace("\\", "/")


def is_maintenance():
    global ROOT_DIR
    return os.path.isfile(os.path.join(ROOT_DIR, "maintenance.txt"))


def get_latest_version():
    # TODO
    return (59, 4)


def get_server_rsa():
    global _SERVER_KEY
    return _SERVER_KEY


_SECRET_KEY: bytes = CONFIG_DATA.main.secret_key.encode("UTF-8")


def get_secret_key():
    global _SECRET_KEY
    return _SECRET_KEY


_BASE_XORPAD: bytes = CONFIG_DATA.advanced.base_xorpad.encode("UTF-8")


def get_base_xorpad():
    global _BASE_XORPAD
    return _BASE_XORPAD


_APPLICATION_KEY: bytes = CONFIG_DATA.advanced.application_key.encode("UTF-8")


def get_application_key():
    global _APPLICATION_KEY
    return _APPLICATION_KEY


def need_xmc_verify():
    global CONFIG_DATA
    return CONFIG_DATA.advanced.verify_xmc


def get_database_url():
    global CONFIG_DATA
    return CONFIG_DATA.database.url


def get_consumer_key():
    global CONFIG_DATA
    return CONFIG_DATA.advanced.consumer_key


def inject_server_info():
    global CONFIG_DATA
    return CONFIG_DATA.download.send_patched_server_info


def load_module_from_file(file: str, modulename: str):
    loader = importlib.machinery.SourceFileLoader(modulename, file)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


_LOGIN_BONUS_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.game.login_bonus)
_login_bonus_module = cast(cfgtype.LoginBonusProtocol, load_module_from_file(_LOGIN_BONUS_FILE, "npps4_login_bonus"))


def get_login_bonus_protocol():
    global _login_bonus_module
    return _login_bonus_module


BADWORDS_CHECK_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.game.badwords)
_badwords_check_module = None


async def contains_badwords(string: str, context):
    global _badwords_check_module

    if _badwords_check_module is None:
        _badwords_check_module = cast(
            cfgtype.BadwordsCheckProtocol, load_module_from_file(BADWORDS_CHECK_FILE, "npps4_badwords_check")
        )

    return await _badwords_check_module.has_badwords(string, context)


BEATMAP_PROVIDER_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.game.beatmaps)
_beatmap_provider_module = None


def get_beatmap_provider_protocol():
    global _beatmap_provider_module

    if _beatmap_provider_module is None:
        _beatmap_provider_module = cast(
            cfgtype.BeatmapProviderProtocol, load_module_from_file(BEATMAP_PROVIDER_FILE, "npps4_beatmap_provider")
        )

    return _beatmap_provider_module


LIVE_UNIT_DROP_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.game.live_unit_drop)
_live_unit_drop_module = None


def get_live_unit_drop_protocol():
    global _live_unit_drop_module

    if _live_unit_drop_module is None:
        _live_unit_drop_module = cast(
            cfgtype.LiveUnitDropProtocol, load_module_from_file(LIVE_UNIT_DROP_FILE, "npps4_live_unit_drop")
        )

    return _live_unit_drop_module


CUSTOM_DOWNLOAD_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.download.custom.file)
_custom_download_backend_module = None


def get_custom_download_protocol():
    global _custom_download_backend_module

    if _custom_download_backend_module is None:
        _custom_download_backend_module = cast(
            cfgtype.DownloadBackendProtocol,
            load_module_from_file(CUSTOM_DOWNLOAD_FILE, "npps4_custom_download_backend"),
        )

    return _custom_download_backend_module


def is_script_mode():
    # Doing "python -m npps4.script" implicitly loads "npps4" module which loads "npps4.config.config".
    # As per Python documentation, the sys.argv[0] will equal to "-m" if the module is being loaded, however
    # endpoint registration happends during loading.
    return (
        hasattr(sys, "ps1")
        or "npps4.script_dummy" in sys.modules
        or (len(sys.argv) > 0 and (sys.argv[0] == "-m" or "alembic" in sys.argv[0].lower()))
    )


def get_server_data_path():
    return os.path.join(ROOT_DIR, CONFIG_DATA.main.server_data)


LIVE_BOX_DROP_FILE = os.path.join(ROOT_DIR, CONFIG_DATA.game.live_box_drop)
_live_box_drop_module = None


def get_live_box_drop_protocol():
    global _live_box_drop_module

    if _live_box_drop_module is None:
        _live_box_drop_module = cast(
            cfgtype.LiveDropBoxProtocol, load_module_from_file(LIVE_BOX_DROP_FILE, "npps4_live_box_drop")
        )

    return _live_box_drop_module
