import sqlalchemy

from . import core
from ... import idol
from ...db import main


async def get(context: idol.SchoolIdolParams, id: int | None = None):
    if isinstance(context, idol.SchoolIdolUserParams):
        id = context.token.user_id
    return await context.db.main.get(main.User, id)


async def create(context: idol.SchoolIdolParams, key: str, passwd: str):
    user = main.User(key=key)
    user.set_passwd(passwd)
    context.db.main.add(user)
    await context.db.main.flush()
    user.invite_code = core.get_invite_code(user.id)
    await context.db.main.flush()
    return user


async def find_by_key(context: idol.SchoolIdolParams, key: str):
    q = sqlalchemy.select(main.User).where(main.User.key == key).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar()
