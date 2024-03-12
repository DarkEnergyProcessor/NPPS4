import base64
import dataclasses
import pickle

import itsdangerous
import sqlalchemy

from . import contexttype
from .. import util
from ..config import config
from ..db import main
from typing import cast

TOKEN_SERIALIZER = itsdangerous.serializer.Serializer(config.get_secret_key(), serializer=pickle)
FIRST_STAGE_TOKEN_MAX_DURATION = 60
SALT_SIZE = 16
TOKEN_SIZE = 16


@dataclasses.dataclass(kw_only=True)
class TokenData:
    client_key: bytes
    server_key: bytes
    user_id: int


async def encapsulate_token(
    context: contexttype.BasicSchoolIdolContext, server_key: bytes, client_key: bytes, user_id: int = 0
):
    salt = util.randbytes(SALT_SIZE)
    token = util.randbytes(TOKEN_SIZE).hex()[:TOKEN_SIZE]
    session = main.Session(
        token=token, user_id=None if user_id == 0 else user_id, client_key=client_key, server_key=server_key
    )
    result = cast(bytes, TOKEN_SERIALIZER.dumps(token, salt))

    context.db.main.add(session)
    await context.db.main.flush()
    return str(base64.urlsafe_b64encode(salt + result), "utf-8")


async def decapsulate_token(context: contexttype.BasicSchoolIdolContext, token_data: str):
    t = util.time()

    # Delete unauthenticated tokens
    q = sqlalchemy.delete(main.Session).where(
        main.Session.user_id == None, main.Session.last_accessed < (t - FIRST_STAGE_TOKEN_MAX_DURATION)
    )
    await context.db.main.execute(q)
    await context.db.main.flush()

    # Delete tokens
    expiry_time = config.get_session_expiry_time()
    if expiry_time > 0:
        q = sqlalchemy.delete(main.Session).where(main.Session.last_accessed < (t - expiry_time))
        await context.db.main.execute(q)
        await context.db.main.flush()

    encoded_data = base64.urlsafe_b64decode(token_data)
    salt, result = encoded_data[:SALT_SIZE], encoded_data[SALT_SIZE:]
    try:
        token: str = TOKEN_SERIALIZER.loads(result, salt)
    except itsdangerous.BadSignature:
        return None

    q = sqlalchemy.select(main.Session).where(main.Session.token == token)
    result = await context.db.main.execute(q)
    session = result.scalar()
    if session is None:
        return None

    session.last_accessed = util.time()
    return TokenData(client_key=session.client_key, server_key=session.server_key, user_id=session.user_id or 0)


async def invalidate_current(context: contexttype.SchoolIdolParams):
    if context.token_text is not None:
        q = sqlalchemy.delete(main.Session).where(main.Session.token == context.token_text)
        await context.db.main.execute(q)
        await context.db.main.flush()
