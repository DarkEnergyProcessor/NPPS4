import sqlalchemy

from .. import const
from .. import idol
from ..db import main
from ..system import advanced
from ..system import item_model
from ..system import reward
from ..system import unit


async def give_all_supporter_units(context: idol.BasicSchoolIdolContext, user: main.User, /):
    q = sqlalchemy.select(unit.unit.Unit.unit_id).where(
        unit.unit.Unit.disable_rank_up > 0, unit.unit.Unit.disable_rank_up < 5
    )
    result = await context.db.unit.execute(q)
    for unit_id in result.scalars():
        item_data = await advanced.deserialize_item_data(
            context, item_model.BaseItem(add_type=const.ADD_TYPE.UNIT, item_id=unit_id, amount=100)
        )
        await reward.add_item(
            context, user, item_data, " 追いかける, ショー・ヘーレーション!", "Oikakeru, Snow Halation!"
        )

    return "Given all supporter members (100x quantity each)."
