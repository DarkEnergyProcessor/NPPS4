import dataclasses

import pydantic

from . import item
from . import unit
from ... import idol
from ... import util
from ...const import ADD_TYPE
from ...idol.system import achievement
from ...idol.system import background
from ...idol.system import museum
from ...idol.system import scenario
from ...idol.system import unit
from ...db import main


@dataclasses.dataclass
class AddResult:
    success: bool
    reason_unit_full: bool = False

    def __nonzero__(self):
        return self.success


class PartyCenterUnitInfo(pydantic.BaseModel):
    unit_owning_user_id: int
    unit_id: int
    exp: int
    next_exp: int
    level: int
    level_limit_id: int
    max_level: int
    rank: int
    max_rank: int
    love: int
    max_love: int
    unit_skill_level: int
    max_hp: int
    favorite_flag: bool
    display_rank: int
    unit_skill_exp: int
    unit_removable_skill_capacity: int
    attribute: int
    smile: int
    cute: int
    cool: int
    is_love_max: bool
    is_level_max: bool
    is_rank_max: bool
    is_signed: bool
    is_skill_level_max: bool
    setting_award_id: int
    removable_skill_ids: list[int] = pydantic.Field(default_factory=list)


class PartyUserInfo(pydantic.BaseModel):
    user_id: int
    name: str
    level: int


class PartyInfo(pydantic.BaseModel):
    user_info: PartyUserInfo
    center_unit_info: PartyCenterUnitInfo
    setting_award_id: int
    available_social_point: int
    friend_status: int


class LiveDeckUnitAttribute(pydantic.BaseModel):
    smile: int
    cute: int
    cool: int


class LiveDeckInfo(pydantic.BaseModel):
    unit_deck_id: int
    total_smile: int
    total_cute: int
    total_cool: int
    total_hp: int
    prepared_hp_damage: int
    unit_list: list[LiveDeckUnitAttribute]


async def add_item(context: idol.BasicSchoolIdolContext, user: main.User, item: item.Item):
    match item.add_type:
        case ADD_TYPE.ITEM:
            match item.item_id:
                case 2:
                    user.social_point = user.social_point + item.amount
                    return AddResult(True)
                case 3:
                    user.game_coin = user.game_coin + item.amount
                    return AddResult(True)
                case 4:
                    user.free_sns_coin = user.free_sns_coin + item.amount
                    return AddResult(True)
                case _:
                    return AddResult(True)  # TODO
        case ADD_TYPE.UNIT:
            unit_cnt = await unit.count_units(context, user, True)
            if unit_cnt < user.unit_max:
                await unit.add_unit(context, user, item.item_id, True)
                return AddResult(True)
            else:
                return AddResult(False, reason_unit_full=True)
        case ADD_TYPE.GAME_COIN:
            user.game_coin = user.game_coin + item.amount
            return AddResult(True)
        case ADD_TYPE.LOVECA:
            user.free_sns_coin = user.free_sns_coin + item.amount
            return AddResult(True)
        case ADD_TYPE.SOCIAL_POINT:
            user.social_point = user.social_point + item.amount
            return AddResult(True)
        # FIXME: Actually check for their return values of these unlocks.
        case ADD_TYPE.BACKGROUND:
            await background.unlock_background(context, user, item.item_id)
            return AddResult(True)
        case ADD_TYPE.SCENARIO:
            await scenario.unlock(context, user, item.item_id)
            return AddResult(True)
        case ADD_TYPE.MUSEUM:
            await museum.unlock(context, user, item.item_id)
            return AddResult(True)
        case _:
            return AddResult(True)  # TODO


async def get_user_guest_party_info(context: idol.BasicSchoolIdolContext, user: main.User) -> PartyInfo:
    party_user_info = PartyUserInfo(user_id=user.id, name=user.name, level=user.level)

    # Get unit center info
    unit_center = await unit.get_unit_center(context, user)
    if unit_center is None:
        raise ValueError("invalid user no center")
    unit_data = await unit.get_unit(context, unit_center.unit_id)
    if unit_data is None:
        raise ValueError("invalid user center")
    unit_info = await unit.get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("invalid user center no info")

    unit_full_data, unit_stats = await unit.get_unit_data_full_info(context, unit_data)
    party_unit_info = PartyCenterUnitInfo(
        unit_owning_user_id=unit_data.id,
        unit_id=unit_data.unit_id,
        exp=unit_full_data.exp,
        next_exp=unit_full_data.next_exp,
        level=unit_full_data.level,
        level_limit_id=unit_data.level_limit_id,
        max_level=unit_data.max_level,
        rank=unit_data.rank,
        max_rank=unit_full_data.max_rank,
        love=unit_data.love,
        max_love=unit_full_data.max_love,
        unit_skill_level=unit_full_data.unit_skill_level,
        max_hp=unit_full_data.max_hp,
        favorite_flag=unit_data.favorite_flag,
        display_rank=unit_data.display_rank,
        unit_skill_exp=unit_data.skill_exp,
        unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
        attribute=unit_info.attribute_id,
        smile=unit_stats.smile,
        cute=unit_stats.pure,
        cool=unit_stats.cool,
        is_love_max=unit_full_data.is_love_max,
        is_level_max=unit_full_data.is_level_max,
        is_rank_max=unit_full_data.is_rank_max,
        is_signed=unit_data.is_signed,
        is_skill_level_max=unit_full_data.is_skill_level_max,
        setting_award_id=user.active_award,
    )

    return PartyInfo(
        user_info=party_user_info,
        center_unit_info=party_unit_info,
        setting_award_id=user.active_award,
        # TODO
        available_social_point=5,
        friend_status=0,
    )
