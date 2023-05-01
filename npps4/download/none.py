import os

from .. import config
from .. import util


def get_server_version():
    return util.parse_sif_version(config.CONFIG_DATA["download"]["none"]["client_version"])


def get_db_path(name: str) -> str:
    path = f"{config.get_data_directory()}/db/{name}.db_"
    if os.path.isfile(path):
        return path

    raise NotImplementedError(f"'none' backend does not automatically load databases! Unable to find '{path}'")


def initialize():
    pass
