import itertools

import sqlalchemy

from . import common
from .. import idol
from ..db import main
from ..db import scenario


async def init(context: idol.BasicSchoolIdolContext, user: main.User):
    for i in itertools.chain(range(1, 4), range(184, 189)):
        sc = main.Scenario(user_id=user.id, scenario_id=i, completed=True)
        context.db.main.add(sc)

    await context.db.main.flush()


async def unlock(context: idol.BasicSchoolIdolContext, user: main.User, scenario_id: int):
    if not await is_unlocked(context, user, scenario_id):
        sc = main.Scenario(user_id=user.id, scenario_id=scenario_id, completed=False)
        context.db.main.add(sc)
        await context.db.main.flush()
        return True

    return False


async def get(context: idol.BasicSchoolIdolContext, user: main.User, scenario_id: int):
    q = sqlalchemy.select(main.Scenario).where(
        main.Scenario.user_id == user.id, main.Scenario.scenario_id == scenario_id
    )
    result = await context.db.main.execute(q)
    return result.scalar()


async def get_all(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Scenario).where(main.Scenario.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


@common.context_cacheable("scenario_valid")
async def valid(context: idol.BasicSchoolIdolContext, scenario_id: int):
    scenario_data = await context.db.scenario.get(scenario.Scenario, scenario_id)
    return scenario_data is not None


async def is_unlocked(context: idol.BasicSchoolIdolContext, user: main.User, scenario_id: int):
    sc = await get(context, user, scenario_id)
    return sc is not None


async def is_completed(context: idol.BasicSchoolIdolContext, user: main.User, scenario_id: int):
    sc = await get(context, user, scenario_id)
    if sc is not None:
        return sc.completed
    return False


async def complete(context: idol.BasicSchoolIdolContext, user: main.User, scenario_id: int):
    sc = await get(context, user, scenario_id)
    if sc is None or sc.completed:
        return False

    sc.completed = True
    await context.db.main.flush()
    return True


async def count_completed(context: idol.BasicSchoolIdolContext, user: main.User):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Scenario)
        .where(main.Scenario.user_id == user.id, main.Scenario.completed == True)
    )
    result = await context.db.main.execute(q)
    return result.scalar() or 0


async def count(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(sqlalchemy.func.count()).select_from(main.Scenario).where(main.Scenario.user_id == user.id)
    result = await context.db.main.execute(q)
    return result.scalar() or 0
