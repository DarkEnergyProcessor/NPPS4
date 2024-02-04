import sqlalchemy

from ... import idol
from ...db import main


async def has_award(context: idol.BasicSchoolIdolContext, user: main.User, award_id: int):
    q = sqlalchemy.select(main.Award).where(main.Award.user_id == user.id, main.Award.award_id == award_id).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar() is not None


async def unlock_award(context: idol.BasicSchoolIdolContext, user: main.User, award_id: int, set_active: bool = False):
    has_bg = await has_award(context, user, award_id)
    if has_bg:
        return False

    bg = main.Award(user_id=user.id, award_id=award_id)
    context.db.main.add(bg)

    if set_active:
        user.active_award = award_id

    await context.db.main.flush()
    return True


async def get_awards(context: idol.SchoolIdolParams, user: main.User):
    q = sqlalchemy.select(main.Award).where(main.Award.user_id == user.id)
    result = await context.db.main.execute(q)
    return result.scalars().all()


async def set_award_active(context: idol.SchoolIdolParams, user: main.User, award_id: int):
    has_bg = await has_award(context, user, award_id)
    if not has_bg:
        return False

    user.active_award = award_id
    await context.db.main.flush()
    return True


async def init(context: idol.SchoolIdolParams, user: main.User):
    await unlock_award(context, user, 1, True)
    await unlock_award(context, user, 23)
