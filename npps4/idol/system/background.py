import dataclasses

import sqlalchemy

from ... import idol
from ...db import main


async def has_background(context: idol.BasicSchoolIdolContext, user: main.User, background_id: int):
    q = (
        sqlalchemy.select(main.Background)
        .where(main.Background.user_id == user.id, main.Background.background_id == background_id)
        .limit(1)
    )
    result = await context.db.main.execute(q)
    return result.scalar() is not None


async def unlock_background(
    context: idol.BasicSchoolIdolContext, user: main.User, background_id: int, set_active: bool = False
):
    has_bg = await has_background(context, user, background_id)
    if has_bg:
        return False

    bg = main.Background(user_id=user.id, background_id=background_id, is_set=set_active)
    context.db.main.add(bg)
    await context.db.main.flush()
    return True


async def get_backgrounds(context: idol.SchoolIdolParams, user: main.User):
    q = sqlalchemy.select(main.Background).where(main.Background.user_id == user.id)
    result = await context.db.main.execute(q)
    return result.scalars().all()


async def set_background_active(context: idol.SchoolIdolParams, user: main.User, background_id: int):
    has_bg = await has_background(context, user, background_id)
    if not has_bg:
        return False

    user.active_background = background_id
    await context.db.main.flush()
    return True
