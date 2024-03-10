import json

import sqlalchemy

from . import item_model
from ... import idol
from ... import util
from ...const import ADD_TYPE
from ...db import main


async def add_item(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    item_data: item_model.Item,
    reason_jp: str,
    reason_en: str | None = None,
    expire: int = 0,
):
    incentive = main.Incentive(
        user_id=user.id,
        add_type=item_data.add_type,
        item_id=item_data.item_id,
        amount=item_data.amount,
        message_jp=reason_jp,
        message_en=reason_en,
        extra_data=json.dumps(item_data.dump_extra_data()),
        expire_date=expire,
    )
    context.db.main.add(incentive)
    await context.db.main.flush()
    return incentive


async def get_presentbox(context: idol.BasicSchoolIdolContext, user: main.User):
    t = util.time()

    # Query non-expire incentives.
    q = sqlalchemy.select(main.Incentive).where(
        main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t)
    )
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def count_presentbox(context: idol.BasicSchoolIdolContext, user: main.User):
    t = util.time()
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Incentive)
        .where(
            main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t)
        )
    )
    qc = await context.db.main.execute(q)
    return qc.scalar() or 0
