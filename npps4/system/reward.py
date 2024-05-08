import enum
import json

import pydantic
import sqlalchemy

from . import item_model
from . import live
from . import live_model
from . import scenario_model
from . import unit_model
from .. import const
from .. import idol
from .. import util
from ..db import main


class RewardCategory(enum.IntEnum):
    ALL = 0
    MEMBERS = 1
    ITEMS = 2


class FilterConfig(pydantic.BaseModel):
    # filter depends on the category:
    # 0. [unused]
    # 1. [rarity, attribute, show not in album?]
    # 2. [list of add types]
    filter: list[int]
    category: RewardCategory


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


def apply_filter[T: sqlalchemy.Select](q: T, filter_config: FilterConfig, /) -> T:
    match filter_config.category:
        case RewardCategory.MEMBERS:
            q = q.where(main.Incentive.add_type == const.ADD_TYPE.UNIT)
            if filter_config.filter[0] > 0:
                q = q.where(main.Incentive.unit_rarity == filter_config.filter[0])
            if filter_config.filter[1] > 0:
                q = q.where(main.Incentive.unit_attribute == filter_config.filter[1])
            # TODO: Not in album filter
        case RewardCategory.ITEMS:
            if len(filter_config.filter) == 1 and filter_config.filter[0] == 0:
                q = q.where(main.Incentive.add_type != const.ADD_TYPE.UNIT)
            else:
                q = q.where(main.Incentive.add_type.in_(filter_config.filter))

    return q


async def get_presentbox(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    filter_config: FilterConfig,
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
    q = apply_filter(q, filter_config)

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


async def count_presentbox(
    context: idol.BasicSchoolIdolContext, /, user: main.User, filter_config: FilterConfig | None = None
):
    t = util.time()
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Incentive)
        .where(main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t))
    )
    if filter_config:
        q = apply_filter(q, filter_config)

    qc = await context.db.main.execute(q)
    return qc.scalar() or 0


async def resolve_incentive(context: idol.BasicSchoolIdolContext, user: main.User, incentive: main.Incentive):
    match incentive.add_type:
        case const.ADD_TYPE.UNIT:
            assert incentive.extra_data is not None
            extra_data = json.loads(incentive.extra_data)
            base_info = {"item_id": incentive.item_id, "amount": incentive.amount}
            if extra_data["is_support_member"]:
                item_data = unit_model.UnitSupportItem.model_validate(base_info | extra_data)
            else:
                item_data = unit_model.UnitItem.model_validate(base_info | extra_data)
        case const.ADD_TYPE.LIVE:
            item_data = live_model.LiveItem(
                item_id=incentive.item_id,
                amount=incentive.amount,
                additional_normal_live_status_list=await live.get_normal_live_clear_status_of_track(
                    context, user, incentive.item_id
                ),
            )
        case const.ADD_TYPE.SCENARIO:
            item_data = scenario_model.ScenarioItem(item_id=incentive.item_id, amount=incentive.amount)
        case _:
            item_data = item_model.Item(
                add_type=const.ADD_TYPE(incentive.add_type), item_id=incentive.item_id, amount=incentive.amount
            )
    return item_data


async def get_incentive(context: idol.BasicSchoolIdolContext, user: main.User, incentive_id: int):
    q = sqlalchemy.select(main.Incentive).where(main.Incentive.user_id == user.id, main.Incentive.id == incentive_id)
    result = await context.db.main.execute(q)
    return result.scalar()


async def remove_incentive(context: idol.BasicSchoolIdolContext, incentive: main.Incentive):
    # TODO: Move to incentive history
    await context.db.main.delete(incentive)
    await context.db.main.flush()
