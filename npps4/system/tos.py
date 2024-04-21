import sqlalchemy

from .. import idol
from ..db import main


async def is_agreed(context: idol.SchoolIdolParams, user: main.User, tos_id: int):
    q = sqlalchemy.select(main.TOSAgree).where(main.TOSAgree.user_id == user.id, main.TOSAgree.tos_id == tos_id)
    result = await context.db.main.execute(q)
    return result.scalar() is not None


async def agree(context: idol.BasicSchoolIdolContext, user: main.User, tos_id: int):
    agree = main.TOSAgree(user_id=user.id, tos_id=tos_id)
    context.db.main.add(agree)
    await context.db.main.flush()
