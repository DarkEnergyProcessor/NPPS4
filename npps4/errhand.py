import hashlib
import os
import pickle

from .config import config

ERROR_DIR = os.path.join(config.get_data_directory(), "errors")
os.makedirs(ERROR_DIR, exist_ok=True)

for file in os.scandir(ERROR_DIR):
    if file.is_file():
        os.remove(file)


def save_error(token: str, tb: list[str]):
    key = hashlib.sha1(token.encode("UTF-8"), usedforsecurity=False).hexdigest()

    with open(os.path.join(ERROR_DIR, key + ".pickle"), "wb") as f:
        pickle.dump(tb, f)


def load_error(token: str) -> list[str] | None:
    key = hashlib.sha1(token.encode("UTF-8"), usedforsecurity=False).hexdigest()
    path = os.path.join(ERROR_DIR, key + ".pickle")

    if os.path.isfile(path):
        with open(path, "rb") as f:
            pickle_data = f.read()
        os.remove(path)
        return pickle.loads(pickle_data)
    return None
