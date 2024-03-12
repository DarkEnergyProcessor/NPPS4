import calendar

import pydantic
import sqlalchemy

from . import item
from .. import idol
from ..config import config
from ..db import main


class LoginBonusCalendar(pydantic.BaseModel):
    day: int
    day_of_the_week: int
    special_day: bool = False
    special_image_asset: str = ""
    received: bool
    ad_received: bool = False
    item: item.item_model.Item


async def has_login_bonus(context: idol.BasicSchoolIdolContext, user: main.User, year: int, month: int, day: int):
    q = sqlalchemy.select(main.LoginBonus).where(
        main.LoginBonus.user_id == user.id,
        main.LoginBonus.year == year,
        main.LoginBonus.month == month,
        main.LoginBonus.day == day,
    )
    result = await context.db.main.execute(q)
    return result.scalar() is not None


async def days_login_bonus(context: idol.BasicSchoolIdolContext, user: main.User, year: int, month: int):
    q = sqlalchemy.select(main.LoginBonus).where(
        main.LoginBonus.user_id == user.id,
        main.LoginBonus.year == year,
        main.LoginBonus.month == month,
    )
    result = await context.db.main.execute(q)
    return set(lb.day for lb in result.scalars())


async def mark_login_bonus(context: idol.BasicSchoolIdolContext, user: main.User, year: int, month: int, day: int):
    lbonus_data = main.LoginBonus(user_id=user.id, year=year, month=month, day=day)
    context.db.main.add(lbonus_data)
    await context.db.main.flush()


async def get_calendar(context: idol.BasicSchoolIdolContext, year: int, month: int):
    weekday, days = calendar.monthrange(year, month)
    login_bonus_protocol = config.get_login_bonus_protocol()
    result: list[LoginBonusCalendar] = []

    for day in range(1, days + 1):
        add_type, item_id, amount, special = await login_bonus_protocol.get_rewards(day, month, year, context)
        dotw = (weekday + day) % 7
        lbonus_calendar = LoginBonusCalendar(
            day=day,
            day_of_the_week=dotw,
            received=False,
            item=item.item_model.Item(add_type=add_type, item_id=item_id, amount=amount),
        )

        if special is not None:
            special_asset = special[1 if context.lang == idol.Language.en else 0] or special[0]
            lbonus_calendar.special_day = True
            lbonus_calendar.special_image_asset = special_asset

        result.append(lbonus_calendar)
    return result


async def get_login_count(context: idol.BasicSchoolIdolContext, user: main.User):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.LoginBonus)
        .where(main.LoginBonus.user_id == user.id)
    )
    qc = await context.db.main.execute(q)
    return qc.scalar() or 0
