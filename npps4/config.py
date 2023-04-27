import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import Cryptodome.PublicKey.RSA
import pydantic

ROOT_DIR = os.path.normpath(os.path.dirname(__file__) + "/..")

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


def get_release_info_keys() -> list[ReleaseInfoData]:
    # TODO
    return []


def get_release_info_key_by_id(id: int) -> bytes | None:
    # TODO
    return None


PERFORM_XMC_VERIFY: bool = CONFIG_DATA["main"]["verify_xmc"]


def need_xmc_verify():
    global PERFORM_XMC_VERIFY
    return PERFORM_XMC_VERIFY
