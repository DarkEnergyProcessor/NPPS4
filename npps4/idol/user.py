from .. import db
from .. import idol
from ..idol import system

from typing import overload


def get(context: idol.SchoolIdolParams, id: int | None = None):
    if isinstance(context, idol.SchoolIdolUserParams):
        id = context.token.user_id
    return context.db.main.get(db.main.User, id)


def create(context: idol.SchoolIdolParams, key: str, passwd: str):
    user = db.main.User(key=key)
    user.set_passwd(passwd)
    context.db.main.add(user)
    context.db.main.flush()
    user.invite_code = system.get_invite_code(user.id)
    context.db.main.flush()
    return user


def find_by_key(context: idol.SchoolIdolParams, key: str):
    user = context.db.main.query(db.main.User).where(db.main.User.key == key).first()
    return user
