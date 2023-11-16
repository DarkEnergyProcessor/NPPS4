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
import pydantic

from typing import Iterable, Protocol, Literal, cast

ROOT_DIR = os.path.normpath(os.path.dirname(__file__) + "/..")
os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)


try:
    with open(os.path.normpath(os.path.join(ROOT_DIR, "config.toml")), "rb") as f:
        CONFIG_DATA = tomllib.load(f)
except IOError as e:
    raise Exception("Unable to load config.toml. Is it present in the project root?") from e

try:
    with open(os.path.join(ROOT_DIR, "server_key.pem"), "rb") as f:
        SERVER_KEY = Cryptodome.PublicKey.RSA.import_key(f.read(), os.environ.get("NPPS_KEY_PASSWORD"))
except IOError as e:
    raise Exception("Unable to load server_key.pem. Is it present in the project root?") from e


def get_data_directory():
    global ROOT_DIR
    return os.path.abspath(os.path.join(ROOT_DIR, CONFIG_DATA["main"]["data_directory"])).replace("\\", "/")


def is_maintenance():
    global ROOT_DIR
    return os.path.isfile(os.path.join(ROOT_DIR, "maintenance.txt"))


def get_latest_version():
    # TODO
    return (59, 4)


def get_server_rsa():
    global SERVER_KEY
    return SERVER_KEY


SECRET_KEY: bytes = CONFIG_DATA["main"]["secret_key"].encode("UTF-8")


def get_secret_key():
    global SECRET_KEY
    return SECRET_KEY


BASE_XORPAD: bytes = CONFIG_DATA["advanced"]["base_xorpad"].encode("UTF-8")
assert len(BASE_XORPAD) == 32


def get_base_xorpad():
    global BASE_XORPAD
    return BASE_XORPAD


APPLICATION_KEY: bytes = CONFIG_DATA["advanced"]["application_key"].encode("UTF-8")
assert len(APPLICATION_KEY) == 32


def get_application_key():
    global APPLICATION_KEY
    return APPLICATION_KEY


class ReleaseInfoData(pydantic.BaseModel):
    id: int
    key: str


PERFORM_XMC_VERIFY: bool = CONFIG_DATA["main"]["verify_xmc"]


def need_xmc_verify():
    global PERFORM_XMC_VERIFY
    return PERFORM_XMC_VERIFY


DATABASE_URL: str = CONFIG_DATA["database"]["url"]


def get_database_url():
    global DATABASE_URL
    return DATABASE_URL


CONSUMER_KEY: str = CONFIG_DATA["advanced"]["consumer_key"]


def get_consumer_key():
    global CONSUMER_KEY
    return CONSUMER_KEY


INJECT_SVINFO: bool = bool(CONFIG_DATA["download"]["send_patched_server_info"])


def inject_server_info():
    global INJECT_SVINFO
    return INJECT_SVINFO


_log_request_response_flag = False


def log_request_response(set: bool | None = None):
    global _log_request_response_flag
    old = _log_request_response_flag
    if set is not None:
        _log_request_response_flag = set

    return old


class LoginBonusProtocol(Protocol):
    async def get_rewards(
        self, day: int, month: int, year: int, context
    ) -> tuple[int, int, int, tuple[str, str | None] | None]:
        ...


def load_module_from_file(file: str, modulename: str):
    loader = importlib.machinery.SourceFileLoader(modulename, file)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


LOGIN_BONUS_FILE = os.path.join(ROOT_DIR, CONFIG_DATA["game"]["login_bonus"])
_login_bonus_module = cast(LoginBonusProtocol, load_module_from_file(LOGIN_BONUS_FILE, "npps4_login_bonus"))


def get_login_bonus_protocol():
    global _login_bonus_module
    return _login_bonus_module


class BadwordsCheckProtocol(Protocol):
    async def has_badwords(self, text: str, context) -> bool:
        ...


BADWORDS_CHECK_FILE = os.path.join(ROOT_DIR, CONFIG_DATA["game"]["badwords"])
_badwords_check_module = cast(
    BadwordsCheckProtocol, load_module_from_file(BADWORDS_CHECK_FILE, "npps4_badwords_check")
)


async def contains_badwords(string: str, context):
    global _badwords_check_module
    return await _badwords_check_module.has_badwords(string, context)


class BeatmapData(Protocol):
    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float  # Beatmap speed multipler
    vanish: Literal[0, 1, 2]  # 0 = Normal; 1 = Note hidden as it approaches; 2 = Note shows just before its timing.


class BeatmapProviderProtocol(Protocol):
    async def get_beatmap_data(self, livejson: str, context) -> Iterable[BeatmapData] | None:
        ...

    async def randomize_beatmaps(self, beatmap: Iterable[BeatmapData], seed: bytes, context) -> Iterable[BeatmapData]:
        ...


BEATMAP_PROVIDER_FILE = os.path.join(ROOT_DIR, CONFIG_DATA["game"]["beatmaps"])
_beatmap_provider_module = None


def get_beatmap_provider_protocol():
    global _beatmap_provider_module

    if _beatmap_provider_module is None:
        _beatmap_provider_module = cast(
            BeatmapProviderProtocol, load_module_from_file(BEATMAP_PROVIDER_FILE, "npps4_beatmap_provider")
        )

    return _beatmap_provider_module
