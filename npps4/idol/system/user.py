import sqlalchemy

from . import core
from ... import idol
from ...idol.system import background
from ...db import main


async def get(context: idol.SchoolIdolParams, id: int):
    if isinstance(context, idol.SchoolIdolUserParams):
        id = context.token.user_id
    else:
        raise ValueError("must specify user id")
    return await context.db.main.get(main.User, id)


async def get_current(context: idol.SchoolIdolUserParams):
    result = await context.db.main.get(main.User, context.token.user_id)
    if result is None:
        raise ValueError("logic error, user is None")
    return result


async def create(context: idol.SchoolIdolParams, key: str, passwd: str):
    user = main.User(key=key)
    user.set_passwd(passwd)
    context.db.main.add(user)
    await context.db.main.flush()
    user.invite_code = core.get_invite_code(user.id)
    await background.unlock_background(context, user, 1, True)
    await context.db.main.flush()
    return user


async def find_by_key(context: idol.SchoolIdolParams, key: str):
    q = sqlalchemy.select(main.User).where(main.User.key == key).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar()
