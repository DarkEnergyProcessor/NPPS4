#!/usr/bin/env python

# If you have "python" as Python 2, then shame on you(r distro).
# If you got syntax error with "match", then shame on you(r distro).
# This code is released under public domain.

import argparse
import base64
import dataclasses
import glob
import http.client
import itertools
import json
import re
import sqlite3
import traceback
import urllib.parse

from typing import Any

try:
    import Cryptodome.Cipher.AES  # type: ignore

    def decrypt_aes(key: bytes, data: bytes) -> bytes:
        aes_obj = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CBC, iv=data[:16])
        data = aes_obj.decrypt(data[16:])
        return data[: -data[-1]]

except ImportError:
    try:
        import Crypto.Cipher.AES  # type: ignore

        def decrypt_aes(key: bytes, data: bytes) -> bytes:
            aes_obj = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv=data[:16])
            data = aes_obj.decrypt(data[16:])
            return data[: -data[-1]]

    except ImportError:
        try:
            import cryptography.hazmat.primitives.ciphers  # type: ignore
            import cryptography.hazmat.primitives.ciphers.algorithms  # type: ignore
            import cryptography.hazmat.primitives.ciphers.modes  # type: ignore

            def decrypt_aes(key: bytes, data: bytes) -> bytes:
                aes_obj = cryptography.hazmat.primitives.ciphers.algorithms.AES(key)
                cbc_obj = cryptography.hazmat.primitives.ciphers.modes.CBC(data[:16])
                cipher = cryptography.hazmat.primitives.ciphers.Cipher(aes_obj, cbc_obj)
                decrypter = cipher.decryptor()
                decrypted_data = decrypter.update(data[16:]) + decrypter.finalize()
                return decrypted_data[: -decrypted_data[-1]]

        except ImportError:
            raise Exception("no PyCryptodomex nor cryptography module")


def make_path(parse_result: urllib.parse.ParseResult):
    path = parse_result.path
    if parse_result.params:
        path = f"{path};{parse_result.params}"
    if parse_result.query:
        path = f"{path};{parse_result.path}"
    return path


def load_content(url: str, *, redircount: int = 0) -> bytes:
    url_obj = urllib.parse.urlparse(url, "file")

    if url_obj.scheme == "file":
        with open(url_obj.netloc + url_obj.path, "rb") as f:
            return f.read()
    elif url_obj.scheme == "http":
        default_port = 80
        http_type = http.client.HTTPConnection
    elif url_obj.scheme == "https":
        default_port = 443
        http_type = http.client.HTTPSConnection
    else:
        raise ValueError(f"Unsupported scheme '{url_obj.scheme}' for '{url}")

    assert url_obj.hostname, "hostname is None"
    http_obj = http_type(url_obj.hostname, url_obj.port or default_port)
    http_obj.request("GET", make_path(url_obj))
    with http_obj.getresponse() as response:
        code = response.getcode()

        if code in (301, 302, 303, 307, 308):
            redircount = redircount + 1
            # Redirect
            if redircount > 5:
                raise RuntimeError(f"'{url}' does not properly setup its redirect")
            newloc = response.getheader("Location")
            if newloc is None:
                raise RuntimeError(f"'{url}' says redirect but no Location header")
            newparse = urllib.parse.urlparse(newloc)
            if not newparse.scheme:
                newparse = newparse._replace(scheme=url_obj.scheme)
            if not newparse.netloc:
                newparse = newparse._replace(netloc=url_obj.netloc)
            return load_content(newparse.geturl(), redircount=redircount)
        if code != 200:
            raise ValueError(f"'{url}' returned {code}")

        return response.read()


PRIMARY_KEY_MATCHER = re.compile(r"PRIMARY KEY \(([^\)]+)\)")


def extract_primary_key(create_sql: str):
    matches = re.search(PRIMARY_KEY_MATCHER, create_sql)
    primary_keys: list[str] = []

    if matches is not None:
        for primary_key in matches.group(1).split(","):
            primary_keys.append(primary_key.strip().replace("`", ""))

    return primary_keys


ADDITIONAL_QUERY = ("release_tag", "_encryption_release_id")


def convert_value_from_release_tag(value: Any):
    match value:
        case bool():
            return "1" if value == True else "NULL"
        case _:
            return repr(value)


def decrypt_db(db: str, release_info: dict[int, str]):
    with sqlite3.connect(db) as conn:
        # Get 'sqlite_master' table
        res = conn.execute("SELECT name, sql FROM 'sqlite_master' WHERE type = 'table'")
        table_name: str
        create_sql: str
        run_these_queries: list[str] = []
        for table_name, create_sql in res.fetchall():
            if "_encryption_release_id" in create_sql:
                primary_keys = extract_primary_key(create_sql)
                query_columns = ", ".join(f"`{s}`" for s in itertools.chain(primary_keys, ADDITIONAL_QUERY))
                res = conn.execute(
                    f"SELECT {query_columns} FROM `{table_name}` WHERE release_tag IS NOT NULL AND _encryption_release_id IS NOT NULL"
                )

                for row in res.fetchall():
                    relid = int(row[-1])
                    if relid in release_info:
                        key = base64.b64decode(release_info[relid])
                        encrypted_row = base64.b64decode(row[-2])
                        decrypted_row: dict[str, Any] = json.loads(decrypt_aes(key, encrypted_row))

                        if len(decrypted_row) > 0:
                            update_values = [
                                f"`{k}` = {convert_value_from_release_tag(v)}" for k, v in decrypted_row.items()
                            ]
                            update_values.extend(("`_encryption_release_id` = NULL", "`release_tag` = NULL"))
                            newvalues = ", ".join(update_values)
                            where = " AND ".join(
                                f"`{primary_key}` = {value!r}" for primary_key, value in zip(primary_keys, row)
                            )
                            run_these_queries.append(f"UPDATE `{table_name}` SET {newvalues} WHERE {where}")

        for query in run_these_queries:
            print(f"{query};")
            conn.execute(query)


DEFAULT_RELEASE_INFO = "https://ll.sif.moe/npps4_dlapi/api/v1/release_info"


@dataclasses.dataclass(kw_only=True)
class ProgramArgs:
    db: list[str] = dataclasses.field(default_factory=list)
    release_info: str = DEFAULT_RELEASE_INFO


def main():
    parser = argparse.ArgumentParser(
        description="Decrypt database rows in-place.", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("db", help="Database to decrypt (support glob)", nargs="+")
    parser.add_argument(
        "--release_info",
        help="Where to get release info keys?",
        default=DEFAULT_RELEASE_INFO,
    )
    args = parser.parse_args(namespace=ProgramArgs())

    # Get release info keys
    release_info = {int(k): v for k, v in json.loads(load_content(args.release_info)).items()}
    for unglobbed_path in args.db:
        for path in glob.glob(unglobbed_path, recursive=True):
            try:
                print(f"-- Decrypting database '{path}'")
                decrypt_db(path, release_info)
            except Exception as e:
                print(f"-- Unable to decrypt database '{path}'")
                print("-- " + "-- ".join(traceback.format_exception(e)))


if __name__ == "__main__":
    main()
