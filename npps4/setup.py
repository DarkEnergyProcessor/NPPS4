import multiprocessing

from . import config

lock = multiprocessing.Lock()


def initialize():
    pass


with lock:
    initialize()
