import asyncio
import collections.abc
import enum
import json

import pydantic
import sqlalchemy

from . import advanced
from . import item_model
from . import live
from . import live_model
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


async def cleanup_incentive(context: idol.BasicSchoolIdolContext, time: int = 0):
    if time == 0:
        time = util.time()

    q = sqlalchemy.delete(main.Incentive).where(main.Incentive.expire_date != 0, main.Incentive.expire_date < time)
    await context.db.main.execute(q)
    await context.db.main.flush()


_currently_cleaning = False


async def try_cleanup_incentive():
    global _currently_cleaning
    if not _currently_cleaning:
        _currently_cleaning = True
        await asyncio.sleep(5)
        async with idol.BasicSchoolIdolContext() as context:
            await cleanup_incentive(context)
        _currently_cleaning = False


async def add_item(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    item_data: item_model.Item,
    reason_jp: str,
    reason_en: str | None = None,
    expire: int = 0,
):
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

    extra_data = item_data.get_extra_data()
    incentive = main.Incentive(
        user_id=user.id,
        add_type=item_data.add_type,
        item_id=item_data.item_id,
        amount=item_data.amount,
        message_jp=reason_jp,
        message_en=reason_en,
        extra_data=(
            json.dumps(extra_data.model_dump(mode="json"), separators=(",", ":")) if extra_data is not None else None
        ),
        expire_date=expire,
    )

    if isinstance(item_data, unit_model.UnitSupportItem):
        incentive.unit_attribute = item_data.attribute
        incentive.unit_rarity = item_data.unit_rarity_id

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
) -> collections.abc.Sequence[main.Incentive]:
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

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
                sqlalchemy.case((main.Incentive.expire_date == 0, 1), else_=0),
                main.Incentive.expire_date.asc(),
                main.Incentive.id,
            )
        else:
            # When ordering by expiry date descending, show no expiration first
            q = q.order_by(
                sqlalchemy.case((main.Incentive.expire_date == 0, 0), else_=1),
                main.Incentive.expire_date.desc(),
                main.Incentive.id.desc(),
            )
    else:
        q = q.order_by(
            main.Incentive.insert_date.asc() if order_ascending else main.Incentive.insert_date.desc(),
            main.Incentive.id.desc(),
        )

    q = q.offset(offset)
    if limit > 0:
        q = q.limit(limit)

    result = await context.db.main.execute(q)
    return list(result.scalars())


async def get_presentbox_simple(
    context: idol.BasicSchoolIdolContext, user: main.User, /
) -> collections.abc.Iterable[main.Incentive]:
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

    t = util.time()

    # Query non-expire incentives.
    q = sqlalchemy.select(main.Incentive).where(
        main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t)
    )
    result = await context.db.main.execute(q)
    return result.scalars()


async def count_presentbox(
    context: idol.BasicSchoolIdolContext, /, user: main.User, filter_config: FilterConfig | None = None
):
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

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
    extra_data = json.loads(incentive.extra_data) if incentive.extra_data is not None else None
    item_data = await advanced.deserialize_item_data(
        context,
        item_model.BaseItem(
            add_type=const.ADD_TYPE(incentive.add_type),
            item_id=incentive.item_id,
            amount=incentive.amount,
            extra_data=extra_data,
        ),
    )
    if isinstance(item_data, live_model.LiveItem):
        item_data.additional_normal_live_status_list = await live.get_normal_live_clear_status_of_track(
            context, user, incentive.item_id
        )
        item_data.additional_training_live_status_list = await live.get_training_live_clear_status_of_track(
            context, user, incentive.item_id
        )
    return item_data


async def get_incentive(context: idol.BasicSchoolIdolContext, user: main.User, incentive_id: int):
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

    q = sqlalchemy.select(main.Incentive).where(main.Incentive.user_id == user.id, main.Incentive.id == incentive_id)
    result = await context.db.main.execute(q)
    return result.scalar()


async def remove_incentive(context: idol.BasicSchoolIdolContext, incentive: main.Incentive):
    # TODO: Move to incentive history
    await context.db.main.delete(incentive)
    await context.db.main.flush()


async def has_at_least_one(
    context: idol.BasicSchoolIdolContext, user: main.User, add_type: const.ADD_TYPE, item_id: int
):
    if context.support_background_task():
        context.add_task(try_cleanup_incentive)

    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Incentive)
        .where(
            main.Incentive.user_id == user.id,
            main.Incentive.add_type == add_type.value,
            main.Incentive.item_id == item_id,
        )
        .limit(1)
    )
    result = await context.db.main.execute(q)
    return (result.scalar() or 0) > 0
