import hashlib
import itertools

import sqlalchemy

from .. import idol
from .. import util
from ..db import main

VALID_CHARACTERS = "".join(map(chr, itertools.chain(range(ord("A"), ord("Z") + 1), range(ord("0"), ord("9") + 1))))


def _a_sha1(t):
    return hashlib.sha1(t.encode("utf-8")).hexdigest().upper()


def generate_passcode_sha1(transfer_id: str, transfer_code: str):
    return _a_sha1(_a_sha1(transfer_id) + transfer_code)


def generate_transfer_code():
    return "".join(util.SYSRAND.choices(VALID_CHARACTERS, k=12))


def has_passcode_issued(user: main.User):
    return user.transfer_sha1 is not None


async def find_user_by_passcode(context: idol.BasicSchoolIdolContext, /, sha1_code: str):
    q = sqlalchemy.select(main.User).where(main.User.transfer_sha1 == sha1_code)
    result = await context.db.main.execute(q)
    return result.scalar()


def swap_credentials(source_user: main.User, target_user: main.User):
    # These handles if the source and target is same.
    key, passwd = source_user.key, source_user.passwd
    source_user.key, source_user.passwd = None, None
    target_user.key, target_user.passwd = key, passwd
