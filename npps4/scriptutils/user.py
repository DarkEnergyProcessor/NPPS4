import argparse
import sqlalchemy

from .. import idol
from ..db import main


async def from_invite(context: idol.BasicSchoolIdolContext, invite_code: int):
    q = sqlalchemy.select(main.User).where(main.User.invite_code == invite_code)
    result = await context.db.main.execute(q)
    return result.scalar()


async def from_id(context: idol.BasicSchoolIdolContext, uid: int):
    return await context.db.main.get(main.User, uid)


def register_args(parser):
    parser.add_argument("-u", "--user-id", type=int, help="User ID.")
    parser.add_argument("-i", "--invite-code", type=int, help="Invite Code.")


async def from_args(context: idol.BasicSchoolIdolContext, args: argparse.Namespace):
    if args.user_id is not None:
        target_user = await from_id(context, args.user_id)
    else:
        target_user = await from_invite(context, args.invite_code)

    if target_user is None:
        raise Exception("no such user")

    return target_user
