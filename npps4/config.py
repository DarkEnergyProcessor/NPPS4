import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT_DIR = os.path.normpath(os.path.dirname(__file__) + "/..")

try:
    with open(os.path.normpath(os.path.join(ROOT_DIR, "config.toml")), "rb") as f:
        CONFIG_DATA = tomllib.load(f)
except IOError as e:
    raise Exception("Unable to load config.toml. Is it present in the project root?") from e


def get_data_directory():
    global ROOT_DIR
    return os.path.abspath(os.path.join(ROOT_DIR, CONFIG_DATA["main"]["data_directory"])).replace("\\", "/")
