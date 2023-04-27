import base64
import json

from . import common
from . import main
from . import live
from . import unit

from .. import config
from .. import util

import sqlalchemy.orm

from typing import TypeVar, Any

_T = TypeVar("_T", bound=common.MaybeEncrypted)


def get_decrypted(session: sqlalchemy.orm.Session, cls: type[_T], id: int) -> _T | None:
    obj = session.get(cls, id)
    if obj is not None and obj._encryption_release_id is not None:
        key = config.get_release_info_key_by_id(obj._encryption_release_id)
        if key is not None:
            session.expunge(obj)
            # Decrypt row
            jsondata = util.decrypt_aes(key, base64.b64decode(obj.release_tag or ""))
            data: dict[str, Any] = json.loads(jsondata)
            for k, v in data.items():
                setattr(obj, k, v)
            obj.release_tag = None
            obj._encryption_release_id = None
    return obj
