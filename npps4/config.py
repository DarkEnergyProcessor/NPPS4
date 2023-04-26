import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import Cryptodome.PublicKey.RSA

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


SECRET_KEY: bytes = CONFIG_DATA["main"]["secret_key"].encode("UTF-8")


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


def get_secret_key():
    global SECRET_KEY
    return SECRET_KEY
