import argparse
import sqlalchemy

from .. import idol
from .. import util
from ..db import main
from ..game import login
from ..system import tos
from ..system import tutorial
from ..system import unit


async def from_invite(context: idol.BasicSchoolIdolContext, invite_code: str):
    q = sqlalchemy.select(main.User).where(main.User.invite_code == invite_code)
    result = await context.db.main.execute(q)
    return result.scalar()


async def from_id(context: idol.BasicSchoolIdolContext, uid: int):
    return await context.db.main.get(main.User, uid)


def register_args(parser):
    parser.add_argument("-u", "--user-id", type=int, help="User ID.")
    parser.add_argument("-i", "--invite-code", type=str, help="Invite Code.")


async def from_args(context: idol.BasicSchoolIdolContext, args: argparse.Namespace):
    if args.user_id is not None:
        target_user = await from_id(context, args.user_id)
    else:
        target_user = await from_invite(context, args.invite_code)

    if target_user is None:
        raise Exception("no such user")

    return target_user


async def simulate_completion(
    context: idol.BasicSchoolIdolContext, /, user: main.User, unit_initial_set_id: int | None = None
):
    await tos.agree(context, user, 1)

    if unit_initial_set_id is None:
        unit_initial_set_id = util.SYSRAND.choice(range(1, 19))

    target = unit_initial_set_id - 1
    unit_ids = login._generate_deck_list(login.INITIAL_UNIT_IDS[target // 9][target % 9])

    units: list[main.Unit] = []
    for uid in unit_ids:
        unit_object = await unit.add_unit_simple(context, user, uid, True)
        if unit_object is None:
            raise RuntimeError("unable to add units")

        units.append(unit_object)

    # Idolize center
    center = units[4]
    await unit.idolize(context, user, center)
    await unit.set_unit_center(context, user, center)

    deck, _ = await unit.load_unit_deck(context, user, 1, True)
    await unit.save_unit_deck(context, user, deck, [u.id for u in units])

    # Simulate tutorial
    await tutorial.phase1(context, user)
    await tutorial.phase2(context, user)
    await tutorial.phase3(context, user)
    await tutorial.finalize(context, user)

    await context.db.main.flush()
