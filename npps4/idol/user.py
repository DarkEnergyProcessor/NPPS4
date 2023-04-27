from .. import db
from .. import idol
from ..idol import system


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
