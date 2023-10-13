import sqlalchemy

from ... import idol
from ...db import main


async def is_agreed(context: idol.SchoolIdolParams, user: main.User):
    agree = await context.db.main.get(main.TOSAgree, user.id)
    return agree is not None


async def agree(context: idol.SchoolIdolParams, user: main.User):
    agree = main.TOSAgree(user_id=user.id)
    context.db.main.add(agree)
    await context.db.main.flush()
