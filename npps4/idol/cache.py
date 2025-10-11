import collections.abc

import sqlalchemy

from . import session
from .. import util
from ..db import main

from typing import cast

ENABLE_CACHE = False


async def load_response(context: session.SchoolIdolParams, endpoint: str):
    if ENABLE_CACHE:
        if isinstance(context, session.SchoolIdolUserParams) and context.nonce > 0:
            assert context.token is not None
            q = sqlalchemy.select(main.RequestCache).where(
                main.RequestCache.user_id == context.token.user_id, main.RequestCache.nonce == context.nonce
            )
            result = await context.db.main.execute(q)

            cache = result.scalar()
            if cache is not None and cache.endpoint == endpoint:
                util.log("Cache for endpoint", endpoint, context.nonce, "FOUND!!")
                return cache.response

        util.log("Cache for endpoint", endpoint, context.nonce, "not found")
    return None


async def store_response(
    context: session.SchoolIdolParams, endpoint: str, response_base: collections.abc.Sequence[int]
):
    if ENABLE_CACHE:
        if isinstance(context, session.SchoolIdolUserParams) and context.nonce > 0:
            assert context.token is not None
            user_id = context.token.user_id
            nonce = context.nonce
            q = sqlalchemy.select(main.RequestCache).where(
                main.RequestCache.user_id == user_id, main.RequestCache.nonce == nonce
            )
            result = await context.db.main.execute(q)

            response = bytes(response_base)
            cache = result.scalar()
            if cache is None:
                cache = main.RequestCache(user_id=user_id, endpoint=endpoint, nonce=nonce, response=response)
                context.db.main.add(cache)
            else:
                cache.endpoint = endpoint
                cache.response = response
            await context.db.main.flush()
            util.log("Stored cache for endpoint", endpoint, context.nonce)


async def clear(context: session.BasicSchoolIdolContext, user_id: int):
    q = sqlalchemy.delete(main.RequestCache).where(main.RequestCache.user_id == user_id)
    result = cast(sqlalchemy.CursorResult, await context.db.main.execute(q))
    return result.rowcount
