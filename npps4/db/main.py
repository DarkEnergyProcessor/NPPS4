import base64
import hashlib
import hmac

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from .. import config
from .. import util
from ..idol.system import core

SALT_SIZE = 16


class User(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    key: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(index=True)
    passwd: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()

    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(default="Kemp")
    level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    previous_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=core.get_next_exp_cumulative(1))
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
    active_deck_index: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)

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


class Background(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    background_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    is_set: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column()
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)


class TOSAgree(common.Base):
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), primary_key=True
    )


class Unit(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    active: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(index=True)
    favorite_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    is_signed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=util.time)

    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    love: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)  # Bond
    rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Non-idolized = 1, idolized = 2
    display_rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Same as rank
    level_limit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitDeck(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    deck_number: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, deck_number),)


class UnitDeckPosition(common.Base):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, primary_key=True)
    deck_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(UnitDeck.id), index=True
    )
    position: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Unit.id), index=True
    )

    __table_args__ = (sqlalchemy.UniqueConstraint(deck_id, unit_id),)


engine = sqlalchemy.ext.asyncio.create_async_engine(config.get_database_url())
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)


def get_sessionmaker():
    global sessionmaker
    return sessionmaker
