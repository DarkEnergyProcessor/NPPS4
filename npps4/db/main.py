import base64
import hashlib
import hmac

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from . import common
from .. import idoltype
from .. import util
from ..config import config
from ..system import core

SALT_SIZE = 16


class User(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    key: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(default=None, index=True)
    passwd: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(default=None)
    locked: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    transfer_sha1: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(default=None, index=True)

    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(default="Kemp")
    bio: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(default="Hello!")
    level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    previous_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    next_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=core.get_next_exp_cumulative(1))
    game_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    free_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    paid_sns_coin: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    social_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=320)
    waiting_unit_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1000)
    energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=25)
    energy_full_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time
    )
    license_live_energy_recoverly_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=60)
    energy_full_need_time: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    over_max_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    training_energy: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=3)
    training_energy_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=3)
    friend_max: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=10)
    invite_code: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        default="", index=True
    )  # Note: We can't mark this field as unique as their computation depends on `id`.
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default_factory=util.time)
    update_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time, onupdate=util.time
    )
    tutorial_state: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    active_deck_index: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    active_background: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    active_award: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    center_unit_owning_user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    live_effort_point_box_spec_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    limited_effort_event_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    current_live_effort_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    current_limited_effort_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)

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


class Session(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    token: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(unique=True)
    user_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    client_key: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()
    server_key: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()
    last_accessed: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time, index=True
    )


class RequestCache(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    endpoint: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    nonce: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    response: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, nonce),)


class Background(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    background_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default_factory=util.time)


class Award(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    award_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default_factory=util.time)


class TOSAgree(common.Base, kw_only=True):
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), primary_key=True
    )
    tos_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, tos_id),)


class Unit(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    active: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(index=True)
    favorite_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    is_signed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default_factory=util.time)

    exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    skill_exp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    max_level: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    love: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)  # Bond
    rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Non-idolized = 1, idolized = 2
    display_rank: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()  # Same as rank
    level_limit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    unit_removable_skill_capacity: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()


class UnitDeck(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    deck_number: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    unit_owning_user_id_1: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_2: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_3: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_4: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_5: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_6: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_7: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_8: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    unit_owning_user_id_9: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, deck_number),)


class UnitSupporter(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, unit_id),)


class Album(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    rank_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    love_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    rank_level_max_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    highest_love_per_unit: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    favorite_point: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0, index=True)
    sign_flag: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)


class Achievement(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    achievement_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    achievement_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)  # for fast lookup
    achievement_filter_category_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        index=True
    )  # for fast lookup
    count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    is_accomplished: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)
    is_reward_claimed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time, index=True
    )
    update_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time, onupdate=util.time, index=True
    )
    end_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)
    is_new: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=True, index=True)
    reset_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    reset_value: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default=0, index=True
    )  # For reset_type > 0

    __table_args__ = (sqlalchemy.UniqueConstraint(achievement_id, user_id),)


class LoginBonus(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    year: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    month: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    day: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, year, month, day),)


class Incentive(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    add_type: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=1)
    message_jp: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(default="")
    message_en: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(default=None)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, default_factory=util.time, index=True
    )
    expire_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)
    extra_data: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(default=None)  # JSON-data
    claimed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False)
    unit_rarity: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(default=None, index=True)
    unit_attribute: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(default=None, index=True)

    def get_message(self, language: idoltype.Language = idoltype.Language.en):
        if language == idoltype.Language.jp:
            return self.message_jp
        else:
            return self.message_en or self.message_jp


class Scenario(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    scenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    completed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, scenario_id),)


class SubScenario(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    subscenario_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    completed: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(default=False, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, subscenario_id),)


class LiveClear(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    difficulty: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)  # for fast lookup
    hi_score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)
    hi_combo_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)
    clear_cnt: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, live_difficulty_id),)


class MuseumUnlock(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    museum_contents_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, museum_contents_id),)


class RemovableSkillInfo(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    unit_removable_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)
    insert_date: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, unit_removable_skill_id),)


class UnitRemovableSkill(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    unit_owning_user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(Unit.id), index=True
    )
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )  # for fast lookup
    unit_removable_skill_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()

    __table_args__ = (sqlalchemy.UniqueConstraint(unit_owning_user_id, unit_removable_skill_id),)


class LiveInProgress(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True, unique=True
    )
    party_user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id)
    )
    lp_factor: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    unit_deck_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    deck_data: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()  # JSON-encoded LiveDeckInfo


class Item(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, item_id),)


class RecoveryItem(common.Base, kw_only=True):
    """LP Recovery item"""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, item_id),)


class ExchangePointItem(common.Base, kw_only=True):
    """Sticker Shop item"""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    exchange_point_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)
    amount: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, exchange_point_id),)


class LocalSerialCodeUsage(common.Base, kw_only=True):
    """Per-user serial code issue"""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    serial_code_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)


class GlobalSerialCodeUsage(common.Base, kw_only=True):
    """Server-wide serial code issue"""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    serial_code_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)


class NormalLiveUnlock(common.Base, kw_only=True):
    """Normal live show unlocks"""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    live_track_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(index=True)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, live_track_id),)


class ExchangeItemLimit(common.Base, kw_only=True):
    """Tracks on bought item in sticker shop."""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    exchange_item_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, default=0)

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, exchange_item_id),)


class NotesListBackup(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)

    crc32: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)  # Fast lookup
    sha256: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column(unique=True)  # Raw SHA256
    notes_list: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()  # GZip compressed notes list


class LiveReplay(common.Base, kw_only=True):
    """Contain live replay data."""

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        common.IDInteger, sqlalchemy.ForeignKey(User.id), index=True
    )
    live_difficulty_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, index=True)
    use_skill: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column()
    timestamp: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)
    notes_crc32: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)
    notes_sha256: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()
    precise_log: sqlalchemy.orm.Mapped[bytes] = sqlalchemy.orm.mapped_column()  # GZip compressed precise score log

    __table_args__ = (sqlalchemy.UniqueConstraint(user_id, live_difficulty_id, use_skill),)


class PlayerRanking(common.Base, kw_only=True):
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, init=False, primary_key=True)
    user_id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger, sqlalchemy.ForeignKey(User.id))
    day: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column()
    score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(common.IDInteger)

    __table_args__ = (
        sqlalchemy.UniqueConstraint(user_id, day),
        sqlalchemy.Index(None, user_id.asc(), day.desc(), score.desc()),
    )


class MigrationFixes(common.Base, kw_only=True):
    revision: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(primary_key=True)


engine = sqlalchemy.ext.asyncio.create_async_engine(config.get_database_url(), connect_args={"autocommit": False})
sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(engine)


def get_sessionmaker():
    global sessionmaker
    return sessionmaker
