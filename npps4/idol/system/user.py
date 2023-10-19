import math

import sqlalchemy

from . import core
from ... import idol
from ... import util
from ...idol.system import achievement
from ...idol.system import background
from ...db import main


async def get(context: idol.SchoolIdolParams, id: int):
    if isinstance(context, idol.SchoolIdolUserParams):
        id = context.token.user_id
    else:
        raise ValueError("must specify user id")
    return await context.db.main.get(main.User, id)


async def get_current(context: idol.SchoolIdolUserParams):
    result = await context.db.main.get(main.User, context.token.user_id)
    if result is None:
        raise ValueError("logic error, user is None")
    return result


async def create(context: idol.SchoolIdolParams, key: str, passwd: str):
    user = main.User(key=key)
    user.set_passwd(passwd)
    context.db.main.add(user)
    await context.db.main.flush()
    user.invite_code = core.get_invite_code(user.id)
    await achievement.init(context, user)
    await background.unlock_background(context, user, 1, True)
    await context.db.main.flush()
    return user


async def find_by_key(context: idol.SchoolIdolParams, key: str):
    q = sqlalchemy.select(main.User).where(main.User.key == key).limit(1)
    result = await context.db.main.execute(q)
    return result.scalar()


def get_current_energy(user: main.User, t: int | None = None):
    if t is None:
        t = util.time()
    difftime = max(user.energy_full_time - t, 0)
    # 1 LP = 6 minutes = 360 seconds
    used_lp = math.ceil(difftime / 360)
    return max(user.energy_max - used_lp, 0)


async def add_exp(context: idol.BasicSchoolIdolContext, user: main.User, exp: int):
    next_exp = core.get_next_exp_cumulative(user.level)
    level_up = False
    over_energy = 0
    max_energy = 0

    user.exp = user.exp + exp
    while user.exp >= next_exp:
        level_up = True
        user.level = user.level + 1
        next_exp = core.get_next_exp_cumulative(user.level)
        max_energy = core.get_energy_by_rank(user.level)
        over_energy = over_energy + max_energy
        # TODO: Achievement

    if level_up:
        t = util.time()
        # Increase max friend
        user.friend_max = core.get_max_friend_by_rank(user.level)
        # Increase master ticket
        user.training_energy_max = core.get_training_energy_by_rank(user.level)
        # Calculate current LP
        current_energy = get_current_energy(user, t)
        # Increase LP
        user.energy_max = max_energy
        # Overflow LP
        user.energy_full_time = t
        user.over_max_energy = current_energy + over_energy

    await context.db.main.flush()
    # TODO: Inform level up data to live show result.
