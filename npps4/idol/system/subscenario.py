import sqlalchemy

from ... import idol
from ...db import main


async def unlock(context: idol.BasicSchoolIdolContext, user: main.User, subscenario_id: int):
    if not await is_unlocked(context, user, subscenario_id):
        sc = main.SubScenario(user_id=user.id, subscenario_id=subscenario_id, completed=False)
        context.db.main.add(sc)
        await context.db.main.flush()
        return True

    return False


async def get(context: idol.BasicSchoolIdolContext, user: main.User, subscenario_id: int):
    q = sqlalchemy.select(main.SubScenario).where(
        main.SubScenario.user_id == user.id, main.SubScenario.subscenario_id == subscenario_id
    )
    result = await context.db.main.execute(q)
    return result.scalar()


async def get_all(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.SubScenario).where(main.SubScenario.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def is_unlocked(context: idol.BasicSchoolIdolContext, user: main.User, subscenario_id: int):
    sc = await get(context, user, subscenario_id)
    return sc is not None


async def is_completed(context: idol.BasicSchoolIdolContext, user: main.User, subscenario_id: int):
    sc = await get(context, user, subscenario_id)
    if sc is not None:
        return sc.completed
    return False


async def complete(context: idol.BasicSchoolIdolContext, user: main.User, subscenario_id: int):
    sc = await get(context, user, subscenario_id)
    if sc is None or sc.completed:
        return False

    sc.completed = True
    await context.db.main.flush()
    return True
