import hashlib
import hmac
import zlib

import pydantic
import sqlalchemy

from . import achievement
from . import award
from . import background
from . import exchange
from . import item
from . import lbonus
from . import live
from . import museum
from . import reward
from . import scenario
from . import subscenario
from . import unit
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
    background: list[int]
    award: list[int]
    unit: list[UnitData]
    deck: list[DeckData]
    sis: list[CommonItemData]  # id = removable_skill_id
    achievement: list[AchievementData]
    login_bonus: list[str]  # string in format: YYYYMMDD
    present_box: list[PresentBoxData]
    scenario: list[int]  # Positive = completed, negative = not completed but availble
    subscenario: list[int]  # Positive = completed, negative = not completed but availble
    museum: list[int]  # List of museum_contents_id
    live_clear: list[LiveClearData]
    normal_live_unlock: list[int]  # List of live_track_id
    items: list[CommonItemData]  # id = item_id
    buff_items: list[CommonItemData]  # id = item_id
    reinforce_items: list[CommonItemData]  # id = item_id
    exchange: list[CommonItemData]  # id = exchange_point_id


class BadSignature(RuntimeError):
    def __init__(self):
        super().__init__("account data bad signature")


async def export_user(
    context: idol.BasicSchoolIdolContext,
    target: main.User,
    /,
    secret_key: bytes | None = None,
    nullify_credentials: bool = False,
):
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
        key=None if nullify_credentials else target.key,
        passwd=None if nullify_credentials else target.passwd,
        transfer_sha1=None if nullify_credentials else target.transfer_sha1,
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

    # Backgrounds
    background_list = [bkg.background_id for bkg in await background.get_backgrounds(context, target)]

    # Awards
    award_list = [aw.award_id for aw in await award.get_awards(context, target)]

    # Iterate all units
    unit_data_list: list[UnitData] = []
    unit_owning_user_id_lookup: dict[int, int] = {}  # [unit_owning_user_id, index+1]
    for unit_data in await unit.get_all_units(context, target, None):
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
    user_data.center_unit_owning_user_id = unit_owning_user_id_lookup[target.center_unit_owning_user_id]

    # Deck
    simple_deck_list = await unit.get_all_deck_simple(context, target)
    deck_data_list = [
        DeckData(
            name=deck[1],
            index=deck[0],
            units=[
                (0 if unit_owning_user_id == 0 else unit_owning_user_id_lookup[unit_owning_user_id])
                for unit_owning_user_id in deck[2]
            ],
        )
        for deck in simple_deck_list
    ]

    # SIS/Removable Skill
    removable_skill_data = await unit.get_removable_skill_info_request(context, target)
    removable_skill_list = [
        CommonItemData(id=info.unit_removable_skill_id, amount=info.total_amount)
        for info in removable_skill_data.owning_info
    ]
    for equip_info in removable_skill_data.equipment_info.values():
        unit_data = unit_data_list[unit_owning_user_id_lookup[equip_info.unit_owning_user_id] - 1]
        unit_data.removable_skills = [d.unit_removable_skill_id for d in equip_info.detail]

    # Achievement
    achievement_list = [
        AchievementData(
            achievement_id=ach.achievement_id,
            count=ach.count,
            # bits: 0 = is_accomplished, 1 = is_reward_claimed, 2 = is_new
            flags=ach.is_accomplished | (ach.is_reward_claimed << 1) | (ach.is_new << 2),
            reset_value=ach.reset_value,
        )
        for ach in await achievement.get_achievements(context, target, None)
    ]

    # Login bonus
    login_bonus_list = [f"{lb[0]:04}{lb[1]:02}{lb[2]:02}" for lb in await lbonus.all_login_bonus(context, target)]

    # Present box
    present_box = await reward.get_presentbox_simple(context, target)
    present_box_list = [
        PresentBoxData(
            add_type=const.ADD_TYPE(pbox.add_type),
            item_id=pbox.item_id,
            amount=pbox.amount,
            message_jp=pbox.message_jp,
            message_en=pbox.message_en,
            expire=pbox.expire_date,
            extra_data=pbox.extra_data,
        )
        for pbox in present_box
    ]

    # Scenario
    scenario_encoded_list = [
        sc.scenario_id * int((-1) ** (not sc.completed)) for sc in await scenario.get_all(context, target)
    ]

    # Subscenario
    subscenario_encoded_list = [
        sc.subscenario_id * int((-1) ** (not sc.completed)) for sc in await subscenario.get_all(context, target)
    ]

    # Museum
    museum_data = await museum.get_museum_info_data(context, target)

    # Live clear
    live_clear_data = [
        LiveClearData(
            live_difficulty_id=lc.live_difficulty_id,
            hi_score=lc.hi_score,
            hi_combo_cnt=lc.hi_combo_cnt,
            clear_cnt=lc.clear_cnt,
        )
        for lc in await live.get_all_live_clear_data(context, target)
    ]

    # Regular items
    items_list_full = await item.get_item_list(context, target)
    general_item_list = [CommonItemData(id=info.item_id, amount=info.amount) for info in items_list_full[0]]
    buff_item_list = [CommonItemData(id=info.item_id, amount=info.amount) for info in items_list_full[1]]
    reinforce_item_list = [CommonItemData(id=info.item_id, amount=info.amount) for info in items_list_full[2]]

    # Exchange
    exchange_points = [
        CommonItemData(id=info.exchange_point_id, amount=info.amount)
        for info in await exchange.get_exchange_point_list(context, target)
        if info.amount > 0
    ]

    # Normal live unlock
    normal_live_unlock = list(await live.get_all_normal_live_unlock(context, target))

    account_data = AccountData(
        user=user_data,
        background=background_list,
        award=award_list,
        unit=unit_data_list,
        sis=removable_skill_list,
        deck=deck_data_list,
        achievement=achievement_list,
        login_bonus=login_bonus_list,
        present_box=present_box_list,
        scenario=scenario_encoded_list,
        subscenario=subscenario_encoded_list,
        museum=museum_data.contents_id_list,
        live_clear=live_clear_data,
        normal_live_unlock=normal_live_unlock,
        items=general_item_list,
        buff_items=buff_item_list,
        reinforce_items=reinforce_item_list,
        exchange=exchange_points,
    )

    json_encoded = account_data.model_dump_json().encode("utf-8")
    salt = util.randbytes(16)
    hash_hmac = hmac.new(secret_key, salt, digestmod=hashlib.sha256)
    hash_hmac.update(json_encoded)

    result = salt + zlib.compress(json_encoded, 9, 31)
    return result, hash_hmac.digest()


def extract_serialized_data(serialized_data: bytes, /, signature: bytes | None, secret_key: bytes | None = None):
    salt = serialized_data[:16]
    json_encoded = zlib.decompress(serialized_data[16:], 31)

    if signature is not None:
        if secret_key is None:
            secret_key = config.get_secret_key()
        hash_hmac = hmac.new(secret_key, salt, digestmod=hashlib.sha256)
        hash_hmac.update(json_encoded)
        if hash_hmac.digest() != signature:
            raise BadSignature()

    return AccountData.model_validate_json(json_encoded)


async def import_user(context: idol.BasicSchoolIdolContext, serialized_data: AccountData, /):
    pass
