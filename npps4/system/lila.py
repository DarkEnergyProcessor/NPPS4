import hashlib
import hmac
import itertools
import json
import zlib

import pydantic
import sqlalchemy

from . import achievement
from . import advanced
from . import award
from . import background
from . import exchange
from . import item
from . import item_model
from . import lbonus
from . import live
from . import museum
from . import reward
from . import scenario
from . import subscenario
from . import unit
from . import unit_model
from . import user
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
    bio: str
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


class PresentBoxData(item_model.BaseItem):
    add_type: const.ADD_TYPE
    item_id: int
    message_jp: str
    message_en: str | None
    expire: int = 0


class LiveClearData(pydantic.BaseModel):
    live_difficulty_id: int
    hi_score: int
    hi_combo_cnt: int
    clear_cnt: int


class CommonItemData(pydantic.BaseModel):
    id: int
    amount: int

    def tuple(self):
        return (self.id, self.amount)

    def has_quantity(self):
        return self.amount > 0


class AccountData(pydantic.BaseModel):
    user: UserData
    background: list[int]
    award: list[int]
    unit: list[UnitData]
    supp_unit: list[CommonItemData]  # id = unit_id
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
    recovery_items: list[CommonItemData]
    exchange: list[CommonItemData]  # id = exchange_point_id


class BadSignature(RuntimeError):
    def __init__(self):
        super().__init__("account data bad signature")


def _already_expired(pbox: main.Incentive, time: int, /):
    if (
        pbox.add_type == const.ADD_TYPE.UNIT
        and pbox.unit_rarity is not None
        and pbox.unit_rarity <= 2
        and pbox.expire_date is None
    ):
        return time > (pbox.insert_date + const.COMMON_UNIT_EXPIRY)
    if pbox.expire_date == 0:
        return False
    return time > pbox.expire_date


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
        bio=target.bio,
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
    user_data.center_unit_owning_user_id = unit_owning_user_id_lookup.get(target.center_unit_owning_user_id, 0)

    # Supporter unit
    supp_unit_list: list[CommonItemData] = [
        CommonItemData(id=info[0], amount=info[1]) for info in await unit.get_all_supporter_unit(context, target)
    ]

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
    login_bonus_list = [f"{lb[2]:04}{lb[1]:02}{lb[0]:02}" for lb in await lbonus.all_login_bonus(context, target)]

    # Present box
    time = util.time()
    present_box = await reward.get_presentbox_simple(context, target)
    present_box_list = [
        PresentBoxData(
            add_type=const.ADD_TYPE(pbox.add_type),
            item_id=pbox.item_id,
            amount=pbox.amount,
            message_jp=pbox.message_jp,
            message_en=pbox.message_en,
            expire=pbox.expire_date,
            extra_data=None if pbox.extra_data is None else json.loads(pbox.extra_data),
        )
        for pbox in present_box
        if _already_expired(pbox, time)
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

    # Recovery items
    recovery_item_list = [
        CommonItemData(id=info.item_id, amount=info.amount) for info in await item.get_recovery_items(context, target)
    ]

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
        supp_unit=supp_unit_list,
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
        recovery_items=recovery_item_list,
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
    target = await user.create(context, None, None)
    target.key = serialized_data.user.key
    target.passwd = serialized_data.user.passwd
    target.transfer_sha1 = serialized_data.user.transfer_sha1
    target.name = serialized_data.user.name
    target.bio = serialized_data.user.bio
    target.exp = serialized_data.user.exp
    target.game_coin = serialized_data.user.coin
    target.free_sns_coin, target.paid_sns_coin = serialized_data.user.sns_coin
    target.social_point = serialized_data.user.friend_pts
    target.unit_max = serialized_data.user.unit_max
    target.waiting_unit_max = serialized_data.user.waiting_unit_max
    target.energy_max = serialized_data.user.energy_max
    target.energy_full_time = serialized_data.user.energy_full_time
    target.license_live_energy_recoverly_time = serialized_data.user.license_live_energy_recoverly_time
    target.energy_full_need_time = serialized_data.user.energy_full_need_time
    target.over_max_energy = serialized_data.user.over_max_energy
    target.training_energy = serialized_data.user.training_energy
    target.training_energy_max = serialized_data.user.training_energy_max
    target.friend_max = serialized_data.user.friend_max
    target.tutorial_state = serialized_data.user.tutorial_state
    target.active_deck_index = serialized_data.user.active_deck_index
    target.active_background = serialized_data.user.active_background
    target.active_award = serialized_data.user.active_award
    target.live_effort_point_box_spec_id = serialized_data.user.live_effort_point_box_spec_id
    target.limited_effort_event_id = serialized_data.user.limited_effort_event_id
    target.current_live_effort_point = serialized_data.user.current_live_effort_point
    target.current_limited_effort_point = serialized_data.user.current_limited_effort_point
    await user.add_exp(context, target, 0)  # To enforce level up

    # Backgrounds
    for bg in serialized_data.background:
        if not await background.has_background(context, target, bg):
            await background.unlock_background(context, target, bg, target.active_background == bg)

    # Awards
    for aw in serialized_data.award:
        if not await award.has_award(context, target, aw):
            await award.unlock_award(context, target, aw, target.active_award == aw)

    # Removable skill (note: must be done first before adding units)
    for removable_skill_id, amount in map(
        CommonItemData.tuple, filter(CommonItemData.has_quantity, serialized_data.sis)
    ):
        await unit.add_unit_removable_skill(context, target, removable_skill_id, amount)

    # Units
    reverse_unit_owning_user_id_lookup: dict[int, int] = {}
    for i, unit_sdata in enumerate(serialized_data.unit, 1):
        unit_data = await unit.add_unit_simple(
            context,
            target,
            unit_sdata.unit_id,
            bool(unit_sdata.flags & 1),
            unit_model.UnitExtraData(
                exp=unit_sdata.exp,
                rank=(unit_sdata.flags >> 3) & 3,
                love=unit_sdata.love,
                skill_exp=unit_sdata.skill_exp,
                unit_removable_skill_capacity=unit_sdata.removable_skill_capacity,
                display_rank=(unit_sdata.flags >> 5) & 3,
                is_signed=bool(unit_sdata.flags & 4),
                removable_skill_ids=tuple(unit_sdata.removable_skills),
            ),
        )
        assert unit_data is not None
        unit_data.favorite_flag = bool(unit_sdata.flags & 2)
        reverse_unit_owning_user_id_lookup[i] = unit_data.id

        for removable_skill_id in unit_sdata.removable_skills:
            await unit.attach_unit_removable_skill(context, unit_data, removable_skill_id)
    if target.center_unit_owning_user_id > 0:
        # Reverse
        target.center_unit_owning_user_id = reverse_unit_owning_user_id_lookup[target.center_unit_owning_user_id]

    # Support Unit
    for unit_id, amount in map(CommonItemData.tuple, filter(CommonItemData.has_quantity, serialized_data.supp_unit)):
        await unit.add_supporter_unit(context, target, unit_id, amount)

    # Deck
    for deck_sdata in serialized_data.deck:
        assert len(deck_sdata.units) == 9
        deck_data, _ = await unit.load_unit_deck(context, target, deck_sdata.index, True)
        deck_data.name = deck_sdata.name
        await unit.save_unit_deck(
            context, target, deck_data, [reverse_unit_owning_user_id_lookup.get(i, 0) for i in deck_sdata.units]
        )

    # Login Bonus
    for datestr in serialized_data.login_bonus:
        await lbonus.mark_login_bonus(context, target, int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))

    # Present Box
    time = util.time()
    for pbox in serialized_data.present_box:
        if pbox.expire != 0 and pbox.expire >= time:
            deserialized_item = await advanced.deserialize_item_data(context, pbox)
            await reward.add_item(context, target, deserialized_item, pbox.message_jp, pbox.message_en, pbox.expire)

    # Scenario
    for scenario_sid in serialized_data.scenario:
        scenario_id = abs(scenario_sid)
        scenario_data = await scenario.get(context, target, scenario_id)
        if scenario_data is None:
            assert await scenario.unlock(context, target, scenario_id)
            scenario_data = await scenario.get(context, target, scenario_id)
            assert scenario_data is not None
        scenario_data.completed = scenario_sid > 0

    # Subscenario
    for subscenario_sid in serialized_data.scenario:
        subscenario_id = abs(subscenario_sid)
        subscenario_data = await subscenario.get(context, target, subscenario_id)
        if subscenario_data is None:
            assert await subscenario.unlock(context, target, subscenario_id)
            subscenario_data = await subscenario.get(context, target, subscenario_id)
            assert subscenario_data is not None
        subscenario_data.completed = subscenario_sid > 0

    # Museum
    for museum_content_id in serialized_data.museum:
        await museum.unlock(context, target, museum_content_id)

    # Normal Live unlock (done this first before live clear)
    for live_track_id in serialized_data.normal_live_unlock:
        await live.unlock_normal_live(context, target, live_track_id)

    # Live Clear tracking
    for live_clear_sdata in serialized_data.live_clear:
        live_clear_data = await live.get_live_clear_data(context, target, live_clear_sdata.live_difficulty_id, True)
        live_clear_data.hi_score = live_clear_sdata.hi_score
        live_clear_data.hi_combo_cnt = live_clear_sdata.hi_combo_cnt
        live_clear_data.clear_cnt = live_clear_sdata.clear_cnt

    # Items
    # TODO: Is this itertools.chain correct?
    for item_id, amount in map(
        CommonItemData.tuple,
        filter(
            CommonItemData.has_quantity,
            itertools.chain(serialized_data.items, serialized_data.buff_items, serialized_data.reinforce_items),
        ),
    ):
        await item.add_item(context, target, item_id, amount)

    # Recovery Items
    for recovery_item_id, amount in map(
        CommonItemData.tuple, filter(CommonItemData.has_quantity, serialized_data.recovery_items)
    ):
        await item.add_recovery_item(context, target, recovery_item_id, amount)

    # Exchange point
    for exchange_point_id, amount in map(
        CommonItemData.tuple, filter(CommonItemData.has_quantity, serialized_data.exchange)
    ):
        await exchange.add_exchange_point(context, target, exchange_point_id, amount)

    # Achievement (note: it must be done last)
    achievements_lookup: dict[int, main.Achievement] = {
        ach.achievement_id: ach for ach in await achievement.get_achievements(context, target, None)
    }
    for ach_sdata in serialized_data.achievement:
        if ach_sdata.achievement_id not in achievements_lookup:
            ach_info = await achievement.get_achievement_info(context, ach_sdata.achievement_id)
            ach_data = await achievement.add_achievement(context, target, ach_info)
        else:
            ach_data = achievements_lookup[ach_sdata.achievement_id]

        ach_data.count = ach_sdata.count
        ach_data.is_accomplished = bool(ach_sdata.flags & 1)
        ach_data.is_reward_claimed = bool(ach_sdata.flags & 2)
        ach_data.is_new = bool(ach_sdata.flags & 4)
        ach_data.reset_value = ach_sdata.reset_value

    await context.db.main.flush()
    return target
