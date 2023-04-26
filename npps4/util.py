import base64
import dataclasses
import hashlib
import hmac
import pickle
import random

import Cryptodome.Cipher.PKCS1_v1_5
import Cryptodome.Cipher.AES
import Cryptodome.Hash.SHA1
import Cryptodome.Util.Padding
import Cryptodome.Signature.pkcs1_15
import itsdangerous.serializer

from . import config

from typing import Literal

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


@dataclasses.dataclass
class TokenData:
    client_key: bytes
    server_key: bytes
    user_id: int


TOKEN_SERIALIZER = itsdangerous.serializer.Serializer(config.get_secret_key(), serializer=pickle)
SALT_SIZE = 8


def encapsulate_token(server_key: bytes, client_key: bytes, user_id: int):
    global TOKEN_SERIALIZER, SALT_SIZE

    data = TokenData(client_key, server_key, user_id)
    salt = randbytes(SALT_SIZE)
    result: bytes = TOKEN_SERIALIZER.dumps(data, salt)  # type: ignore
    return str(base64.b64encode(salt + result), "UTF-8")


def decapsulate_token(token_data: str):
    global TOKEN_SERIALIZER, SALT_SIZE

    token = base64.b64decode(token_data)
    salt, result = token[:SALT_SIZE], token[SALT_SIZE:]
    try:
        data: TokenData = TOKEN_SERIALIZER.loads(result, salt)
        return data
    except itsdangerous.BadSignature:
        return None


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
