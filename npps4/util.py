import base64
import dataclasses
import pickle
import random

import Cryptodome.Hash.SHA1
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


def sign_message(content: bytes, request_xmc: bytes | None):
    sha1 = Cryptodome.Hash.SHA1.new(content)
    if request_xmc is not None:
        sha1.update(request_xmc)
    sign = Cryptodome.Signature.pkcs1_15.new(config.get_server_rsa())
    return str(base64.b64encode(sign.sign(sha1)), "UTF-8")


@dataclasses.dataclass
class TokenData:
    client_key: bytes
    server_key: bytes
    user_id: int


TOKEN_SERIALIZER = itsdangerous.serializer.Serializer(config.get_secret_key())
SALT_SIZE = 8


def encapsulate_token(server_key: bytes, client_key: bytes, user_id: int):
    global TOKEN_SERIALIZER, SALT_SIZE

    data = TokenData(client_key, server_key, user_id)
    encoded_data = pickle.dumps(data)
    salt = randbytes(SALT_SIZE)
    result: bytes = TOKEN_SERIALIZER.dumps(encoded_data, salt)
    return str(base64.b64encode(salt + result), "UTF-8")


def decapsulate_token(token_data: str):
    global TOKEN_SERIALIZER, SALT_SIZE

    token = base64.b64decode(token_data)
    salt, result = token[:SALT_SIZE], token[SALT_SIZE:]
    try:
        encoded_data: bytes = TOKEN_SERIALIZER.loads(result, salt)
        data: TokenData = pickle.loads(encoded_data)
        return data
    except itsdangerous.BadSignature:
        return None
