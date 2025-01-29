import base64
import json

from . import common
from .. import release_key
from .. import util

import sqlalchemy.ext.asyncio

from typing import Any


async def get_decrypted_row[_T: common.MaybeEncrypted](
    session: sqlalchemy.ext.asyncio.AsyncSession, cls: type[_T], id: int
) -> _T | None:
    obj = await session.get(cls, id)
    return decrypt_row(session, obj)


def decrypt_row[_T: common.MaybeEncrypted](session: sqlalchemy.ext.asyncio.AsyncSession, obj: _T | None) -> _T | None:
    if obj is not None and obj._encryption_release_id is not None:
        key = release_key.get(obj._encryption_release_id)

        if key is None:
            return None
        else:
            session.expunge(obj)

            # Decrypt row
            jsondata = util.decrypt_aes(base64.b64decode(key), base64.b64decode(obj.release_tag or ""))
            data: dict[str, Any] = json.loads(jsondata)
            for k, v in data.items():
                setattr(obj, k, v)

            obj.release_tag = None
            obj._encryption_release_id = None

    return obj
