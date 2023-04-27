import base64
import hashlib
import hmac
import re

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

from . import common
from .. import config
from .. import util
from ..idol import system

SALT_SIZE = 16
SNAKECASE_RE1 = re.compile("(.)([A-Z][a-z]+)")
SNAKECASE_RE2 = re.compile("__([A-Z])")
SNAKECASE_RE3 = re.compile("([a-z0-9])([A-Z])")


class Base(sqlalchemy.orm.DeclarativeBase):
    @sqlalchemy.orm.declared_attr.directive
    def __tablename__(cls):
        name = cls.__name__
        name = re.sub(SNAKECASE_RE1, r"\1_\2", name)
        name = re.sub(SNAKECASE_RE2, r"_\1", name)
        name = re.sub(SNAKECASE_RE3, r"\1_\2", name)
        return name.lower()


class User(Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    key: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String, index=True)
    passwd: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(common.String)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(common.String, default="Kemp")
    level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    previous_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=system.get_next_exp_cumulative(1))
    game_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    free_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    paid_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    social_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=120)
    waiting_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1000)
    energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=25)
    energy_full_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    license_live_energy_recoverly_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=60)
    energy_full_need_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    over_max_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    training_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    training_energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    friend_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    invite_code: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0, index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    update_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)
    tutorial_state: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)

    def set_passwd(self, passwd: str):
        salt = util.randbytes(SALT_SIZE)
        hmac_hash = hmac.new(salt, passwd.encode("UTF-8"), digestmod=hashlib.sha512).digest()
        result = salt + hmac_hash[SALT_SIZE:]
        self.passwd = str(base64.b64encode(result), "UTF-8")

    def check_passwd(self, passwd: str):
        if self.passwd is None:
            return False
        result = base64.b64decode(self.passwd)
        salt = result[:SALT_SIZE]
        hmac_hash = hmac.new(salt, passwd.encode("UTF-8"), digestmod=hashlib.sha512).digest()
        return result[SALT_SIZE:] == hmac_hash[SALT_SIZE:]

    @property
    def friend_id(self):
        return "%09d" % self.invite_code


engine: sqlalchemy.Engine | None = None
scoped_session: sqlalchemy.orm.scoped_session[sqlalchemy.orm.Session] | None = None


def get_session():
    global engine, scoped_session
    if engine is None or scoped_session is None:
        engine = sqlalchemy.create_engine(config.get_database_url(), connect_args={"check_same_thread": False})
        sessionmaker = sqlalchemy.orm.sessionmaker()
        sessionmaker.configure(binds={Base: engine})
        scoped_session = sqlalchemy.orm.scoped_session(sessionmaker)
    session = scoped_session()
    return session
