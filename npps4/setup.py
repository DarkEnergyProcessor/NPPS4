import multiprocessing

from .config import config

lock = multiprocessing.Lock()


def initialize():
    pass


with lock:
    initialize()
