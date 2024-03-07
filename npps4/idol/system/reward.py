import dataclasses

import sqlalchemy

from . import item_model
from ... import idol
from ... import util
from ...const import ADD_TYPE
from ...db import main


@dataclasses.dataclass
class RewardUnitData:
    max_level: int
    rank: int
    display_rank: int
    unit_removable_skill_capacity: int
    is_signed: bool = False
    exp: int = 0
    skill_exp: int = 0
    love: int = 0
    level_limit_id: int = 0


async def _add_item_internal(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    item_data: item_model.Item,
    reason_jp: str,
    reason_en: str | None = None,
    expire: int = 0,
):
    incentive = main.Incentive(
        user_id=user.id, add_type=item_data.add_type, item_id=item_data.item_id, amount=item_data.amount
    )
    incentive.set_message(reason_jp, reason_en)
    context.db.main.add(incentive)
    await context.db.main.flush()
    return incentive


def add_item(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    item_data: item_model.Item,
    reason_jp: str,
    reason_en: str | None = None,
    expire: int = 0,
):
    if item_data.add_type == ADD_TYPE.UNIT:
        raise ValueError("Use 'add_unit' to add unit to present box")

    return _add_item_internal(context, user, item_data, reason_jp, reason_en, expire)


async def add_unit(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    item_data: item_model.Item,
    unit_data: RewardUnitData,
    reason_jp: str,
    reason_en: str | None = None,
    expire: int = 0,
):
    if item_data.add_type != ADD_TYPE.UNIT:
        raise ValueError("Use 'add_item' to add other items to present box")

    incentive = await _add_item_internal(context, user, item_data, reason_jp, reason_en, expire)
    incentive_unit = main.IncentiveUnitOption(
        id=incentive.id,
        unit_id=item_data.item_id,
        is_signed=unit_data.is_signed,
        exp=unit_data.exp,
        skill_exp=unit_data.skill_exp,
        max_level=unit_data.max_level,
        love=unit_data.love,
        rank=unit_data.rank,
        display_rank=unit_data.display_rank,
        level_limit_id=unit_data.level_limit_id,
        unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
    )
    context.db.main.add(incentive_unit)
    await context.db.main.flush()
    return incentive, incentive_unit


async def get_presentbox(context: idol.BasicSchoolIdolContext, user: main.User):
    t = util.time()
    # Find out expired units
    q = sqlalchemy.select(main.Incentive).where(
        main.Incentive.user_id == user.id,
        main.Incentive.add_type == ADD_TYPE.UNIT,
        main.Incentive.expire_date != 0,
        main.Incentive.expire_date < t,
    )
    result = await context.db.main.execute(q)
    # Delete incentive unit option
    for incentive in result.scalars():
        incentive_unit = await context.db.main.get(main.IncentiveUnitOption, incentive.id)
        if incentive_unit is not None:
            await context.db.main.delete(incentive_unit)
    # Delete incentive
    q = sqlalchemy.delete(main.Incentive).where(main.Incentive.expire_date != 0, main.Incentive.expire_date < t)
    await context.db.main.execute(q)

    # Query non-expire incentives.
    q = sqlalchemy.select(main.Incentive).where(
        main.Incentive.user_id == user.id, (main.Incentive.expire_date == 0) | (main.Incentive.expire_date >= t)
    )
    result = await context.db.main.execute(q)
    incentive_list: list[tuple[main.Incentive, main.IncentiveUnitOption | None]] = []
    for incentive in result.scalars():
        incentive_unit = None

        if incentive.add_type == ADD_TYPE.UNIT:
            incentive_unit = await context.db.main.get(main.IncentiveUnitOption, incentive.id)

        incentive_list.append((incentive, incentive_unit))

    return incentive_list


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
