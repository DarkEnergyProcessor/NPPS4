import sqlalchemy

from .. import idol
from ..db import main
from ..system import unit


async def give_all_supporter_units(context: idol.BasicSchoolIdolContext, user: main.User, /):
    q = sqlalchemy.select(unit.unit.Unit.unit_id).where(
        unit.unit.Unit.disable_rank_up > 0, unit.unit.Unit.disable_rank_up < 5
    )
    result = await context.db.unit.execute(q)
    for unit_id in result.scalars():
        await unit.add_supporter_unit(context, user, unit_id, 100)

    return "Given all supporter members (100x quantity each)."
