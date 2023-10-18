import sqlalchemy

from . import unit
from . import user
from ... import idol
from ...db import main


async def phase1(context: idol.BasicSchoolIdolContext, user: main.User):
    user.tutorial_state = 1


async def phase2(context: idol.BasicSchoolIdolContext, user: main.User):
    user.tutorial_state = 2


async def phase3(context: idol.BasicSchoolIdolContext, u: main.User):
    # G +37000, not sure why
    u.game_coin = u.game_coin + 37000
    # Friend Points +5
    u.social_point = u.social_point + 5
    # Add EXP
    await user.add_exp(context, u, 11)
    # Reine Saeki
    await unit.add_unit(context, u, 13, True)
    # Akemi Kikuchi
    await unit.add_unit(context, u, 9, True)
    # Bond calculation
    await unit.add_love_by_deck(context, u, u.active_deck_index, 34)
    u.tutorial_state = 3


async def finalize(context: idol.BasicSchoolIdolContext, u: main.User):
    pass
