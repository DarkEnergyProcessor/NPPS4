import base64
import datetime as datetimelib
import hashlib
import hmac
import itertools
import logging
import random
import time as timelib

import Cryptodome.Cipher.PKCS1_v1_5
import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA1
import Cryptodome.Util.Padding
import Cryptodome.Signature.pkcs1_15
import pydantic

from .config import config

from typing import Any, TypeVar, cast

SYSRAND = random.SystemRandom()


def randbytes(n: int):
    global SYSRAND
    return SYSRAND.randbytes(n)


def parse_sif_version(version: str):
    v = version.split(".", 1)
    return int(v[0]), int(v[1])


def sif_version_string(version: tuple[int, int]):
    return "%d.%d" % version


def sign_message(content: bytes, request_xmc_hex: str | None):
    sha1 = Cryptodome.Hash.SHA1.new(content)
    if request_xmc_hex is not None:
        sha1.update(request_xmc_hex.encode("UTF-8"))
    sign = Cryptodome.Signature.pkcs1_15.new(config.get_server_rsa())
    return str(base64.b64encode(sign.sign(sha1)), "UTF-8")


def decrypt_rsa(data: bytes):
    pkcs = Cryptodome.Cipher.PKCS1_v1_5.new(config.get_server_rsa())
    return pkcs.decrypt(data, None)


def decrypt_aes(key: bytes, data: bytes):
    aes = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CBC, iv=data[:16])
    data = aes.decrypt(data[16:])
    return data[: -data[-1]]


def xorbytes(a: bytes, b: bytes):
    if len(a) != len(b):
        raise ValueError("size does not match")
    return bytes(c ^ d for c, d in zip(a, b))


def hmac_sha1(message: bytes, key: bytes):
    digest = hmac.new(key, message, digestmod=hashlib.sha1)
    return digest.digest()


def time():
    return int(timelib.time())


NPPS4_LOGGER = logging.getLogger("npps4")
NPPS4_LOGGER.addHandler(logging.StreamHandler())
NPPS4_LOGGER.setLevel(logging.DEBUG)


def log(*args: object, severity: int = logging.DEBUG, e: Exception | None = None):
    NPPS4_LOGGER.log(severity, " ".join(map(str, args)), exc_info=e)


def stub(module: str, action: str, request: Any = None, /):
    if request:
        log(f"STUB /{module}/{action} {repr(request)}", severity=logging.WARNING)
    else:
        log(f"STUB /{module}/{action}", severity=logging.WARNING)


TIMEZONE_JST = datetimelib.timezone(datetimelib.timedelta(hours=9))


def datetime(ts: int | None = None):
    ts = time() if ts is None else ts
    return datetimelib.datetime.fromtimestamp(ts, TIMEZONE_JST)


def timestamp_to_datetime(ts: int | None = None):
    ts = time() if ts is None else ts
    dtobj = datetime(ts)
    return dtobj.strftime("%Y-%m-%d %H:%M:%S")


def datetime_to_timestamp(dt: str):
    # The +09:00:00 is required so Python treat it as JST!
    timestr = dt.strip() + " +09:00:00"
    try:
        dtobj = datetimelib.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        dtobj = datetimelib.datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S %z")
    return int(dtobj.timestamp())


_T = TypeVar("_T")
_E = TypeVar("_E", bound=Exception)


def ensure_no_none(list_to: list[_T | None], exc: type[_E] = Exception, *args) -> list[_T]:
    if None in list_to:
        raise exc(*args)

    return cast(list[_T], list_to)


class _MeasureClass:
    def __init__(self, name: str, severity: int):
        self.t = 0
        self.name = name
        self.severity = severity

    def __enter__(self):
        self.t = timelib.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        t = ((self.t - timelib.perf_counter_ns()) // 1000) / 1000000

        if exc_type is None:
            log(f"Measuring performance of '{self.name}' took {t} seconds.", severity=self.severity)

        return None


def measure(name: str = "", severity: int = logging.DEBUG):
    return _MeasureClass(name, severity)


def shallow_dump(model: pydantic.BaseModel, /):
    keys = itertools.chain(model.__class__.model_fields.keys(), model.model_computed_fields.keys())
    return {k: getattr(model, k) for k in keys}


def java_hash_code(string: str):
    h = 0
    for s in string:
        h = (h * 31 + ord(s)) & 0xFFFFFFFF
    return h
