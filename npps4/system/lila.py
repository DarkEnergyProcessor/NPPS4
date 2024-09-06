import hashlib
import hmac
import zlib

import pydantic
import sqlalchemy

from .. import const
from .. import idol
from .. import util
from ..config import config
from ..db import main


class UserData(pydantic.BaseModel):
    key: str | None
    passwd: str | None
    transfer_sha1: str | None
    name: str
    exp: int
    coin: int
    sns_coin: list[int]  # index 1 = free, index 2 = paid
    friend_pts: int
    unit_max: int
    waiting_unit_max: int
    energy_max: int
    energy_full_time: int
    license_live_energy_recoverly_time: int
    energy_full_need_time: int
    over_max_energy: int
    training_energy: int
    training_energy_max: int
    friend_max: int
    tutorial_state: int
    active_deck_index: int
    active_background: int
    active_award: int
    center_unit_owning_user_id: int = 0  # Note: Based on 1-based index of serialized UnitData, 0 means not set
    live_effort_point_box_spec_id: int
    limited_effort_event_id: int
    current_live_effort_point: int
    current_limited_effort_point: int


class UnitData(pydantic.BaseModel):
    unit_id: int
    flags: int  # bits: 0 = active, 1 = fav. flag, 2 = signed, 3-4 = rank, 5-6 = display rank
    exp: int
    skill_exp: int
    max_level: int
    love: int
    level_limit_id: int
    removable_skill_capacity: int
    removable_skills: list[int]


class DeckData(pydantic.BaseModel):
    name: str
    index: int
    units: list[int]  # Note: Based on 1-based index of serialized UnitData, 0 means not set


class AchievementData(pydantic.BaseModel):
    achievement_id: int
    count: int
    flags: int  # bits: 0 = is_accomplished, 1 = is_reward_claimed, 2 = is_new
    reset_value: int  # For reset_type > 0


class PresentBoxData(pydantic.BaseModel):
    add_type: const.ADD_TYPE
    item_id: int
    amount: int
    message_jp: str
    message_en: str | None
    expire: int = 0
    extra_data: str | None  # JSON-data


class LiveClearData(pydantic.BaseModel):
    live_difficulty_id: int
    hi_score: int
    hi_combo_cnt: int
    clear_cnt: int


class CommonItemData(pydantic.BaseModel):
    id: int
    amount: int


class AccountData(pydantic.BaseModel):
    user: UserData
    tos: list[int]
    background: list[int]
    award: list[int]
    unit: list[UnitData]
    deck: list[DeckData]
    achievement: list[AchievementData]
    login_bonus: list[str]  # string in format: YYYYMMDD
    present_box: list[PresentBoxData]
    scenario: list[int]  # Positive = completed, negative = not completed but availble
    subscenario: list[int]  # Positive = completed, negative = not completed but availble
    museum: list[int]  # List of museum_contents_id
    live: list[LiveClearData]
    sis: list[CommonItemData]  # id = removable_skill_id
    items: list[CommonItemData]  # id = item_id, for add_type 1000
    exchange: list[CommonItemData]  # id = exchange_point_id
    normal_live_unlock: list[int]  # List of live_track_id


async def export_user(context: idol.BasicSchoolIdolContext, target: main.User, /, secret_key: bytes | None = None):
    """
    Export user data to JSON which can be imported back by "compatible" implementation.

    Note that it returns 2 values, the zlib-compressed JSON bytes and the signature of the **uncompressed** data.
    For security reasons, signature is required for data importing unless server configured otherwise.

    The 1st return value is bytes consist of 16-byte salt + zlib-compressed JSON data.
    The 2nd return value is HMAC-SHA256 hash of the salt + uncompressed JSON data with the HMAC key set to server key.
    """
    if secret_key is None:
        secret_key = config.get_secret_key()

    user_data = UserData(
        key=target.key,
        passwd=target.passwd,
        transfer_sha1=target.transfer_sha1,
        name=target.name,
        exp=target.exp,
        coin=target.game_coin,
        sns_coin=[target.free_sns_coin, target.paid_sns_coin],
        friend_pts=target.social_point,
        unit_max=target.unit_max,
        waiting_unit_max=target.waiting_unit_max,
        energy_max=target.energy_max,
        energy_full_time=target.energy_full_time,
        license_live_energy_recoverly_time=target.license_live_energy_recoverly_time,
        energy_full_need_time=target.energy_full_need_time,
        over_max_energy=target.over_max_energy,
        training_energy=target.training_energy,
        training_energy_max=target.training_energy_max,
        friend_max=target.friend_max,
        tutorial_state=target.tutorial_state,
        active_deck_index=target.active_deck_index,
        active_background=target.active_background,
        active_award=target.active_award,
        live_effort_point_box_spec_id=target.live_effort_point_box_spec_id,
        limited_effort_event_id=target.limited_effort_event_id,
        current_live_effort_point=target.current_live_effort_point,
        current_limited_effort_point=target.current_limited_effort_point,
    )

    # Iterate all units
    unit_data_list: list[UnitData] = []
    unit_owning_user_id_lookup: dict[int, int] = {}
    q = sqlalchemy.select(main.Unit).where(main.Unit.user_id == target.id)
    result = await context.db.main.execute(q)
    for unit_data in result.scalars():
        unit_data_serialized = UnitData(
            unit_id=unit_data.unit_id,
            # bits: 0 = active, 1 = fav. flag, 2 = signed, 3-4 = rank, 5-6 = display rank
            flags=unit_data.active
            | (unit_data.favorite_flag << 1)
            | (unit_data.is_signed << 2)
            | (unit_data.rank << 3)
            | (unit_data.display_rank << 5),
            exp=unit_data.exp,
            skill_exp=unit_data.skill_exp,
            max_level=unit_data.max_level,
            love=unit_data.love,
            level_limit_id=unit_data.level_limit_id,
            removable_skill_capacity=unit_data.unit_removable_skill_capacity,
            removable_skills=[],
        )
        unit_data_list.append(unit_data_serialized)
        unit_owning_user_id_lookup[unit_data.id] = len(unit_data_list)

    account_data = AccountData(
        user=user_data,
        tos=[],
        background=[],
        award=[],
        unit=unit_data_list,
        deck=[],
        achievement=[],
        login_bonus=[],
        present_box=[],
        scenario=[],
        subscenario=[],
        museum=[],
        live=[],
        sis=[],
        items=[],
        exchange=[],
        normal_live_unlock=[],
    )

    json_encoded = account_data.model_dump_json().encode("utf-8")
    salt = util.randbytes(16)
    hash_hmac = hmac.new(secret_key, digestmod=hashlib.sha256)
    hash_hmac.update(json_encoded)

    result = salt + zlib.compress(json_encoded, 9, 31)
    return result, hash_hmac.digest()


async def import_user(context: idol.BasicSchoolIdolContext, serialized_data: bytes, /, signature: bytes):
    pass
