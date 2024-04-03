import json

import sqlalchemy

from . import item_model
from .. import idol
from .. import util
from ..const import ADD_TYPE
from ..db import main


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


async def get_presentbox(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    add_type_filter: list[int] | None = None,
    offset: int = 0,
    limit: int = 1000,
    order_ascending: bool = False,
    order_expiry_date: bool = False,
):
    t = util.time()

    # Query non-expire incentives.
    q = sqlalchemy.select(main.Incentive).where(
        main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t)
    )
    if add_type_filter:
        q = q.where(main.Incentive.add_type.in_(add_type_filter))
    if order_expiry_date:
        if order_ascending:
            # When ordering by expiry date ascending, show no expiration last
            q = q.order_by(
                sqlalchemy.case((main.Incentive.expire_date == 0, 1), else_=0), main.Incentive.expire_date.asc()
            )
        else:
            # When ordering by expiry date descending, show no expiration first
            q = q.order_by(
                sqlalchemy.case((main.Incentive.expire_date == 0, 0), else_=1), main.Incentive.expire_date.desc()
            )
    else:
        q = q.order_by(main.Incentive.insert_date.asc() if order_ascending else main.Incentive.insert_date.desc())

    q = q.offset(offset).limit(limit)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def count_presentbox(context: idol.BasicSchoolIdolContext, user: main.User):
    t = util.time()
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Incentive)
        .where(main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t))
    )
    qc = await context.db.main.execute(q)
    return qc.scalar() or 0
