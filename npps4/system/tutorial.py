from . import unit
from . import user
from .. import idol
from ..db import main
from ..db import game_mater


async def phase1(context: idol.BasicSchoolIdolContext, u: main.User):
    u.tutorial_state = 1


async def phase2(context: idol.BasicSchoolIdolContext, u: main.User):
    u.tutorial_state = 2


async def phase3(context: idol.BasicSchoolIdolContext, u: main.User):
    # G +36400 + 600
    u.game_coin = u.game_coin + game_mater.GAME_SETTING.initial_game_coin + 600
    # Friend Points +5
    u.social_point = u.social_point + game_mater.GAME_SETTING.live_social_point_for_others
    # Add EXP
    await user.add_exp(context, u, 11)
    # Reine Saeki
    await unit.add_unit_simple(context, u, 13, True)
    # Akemi Kikuchi
    await unit.add_unit_simple(context, u, 9, True)
    # Bond calculation
    await unit.add_love_by_deck(context, u, u.active_deck_index, 34)
    u.tutorial_state = 3


async def finalize(context: idol.BasicSchoolIdolContext, u: main.User):
    u.tutorial_state = -1
