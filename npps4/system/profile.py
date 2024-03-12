import pydantic

from . import museum
from . import unit
from .. import idol
from .. import util
from ..db import main


class ProfileUnitInfo(pydantic.BaseModel):
    unit_owning_user_id: int
    unit_id: int
    exp: int
    next_exp: int
    level: int
    max_level: int
    level_limit_id: int
    rank: int
    max_rank: int
    love: int
    max_love: int
    unit_skill_exp: int
    unit_skill_level: int
    max_hp: int
    unit_removable_skill_capacity: int
    favorite_flag: bool
    display_rank: int
    is_rank_max: bool
    is_love_max: bool
    is_level_max: bool
    is_signed: bool
    is_skill_level_max: bool
    is_removable_skill_capacity_max: bool
    insert_date: str
    total_smile: int
    total_cute: int
    total_cool: int
    total_hp: int
    removable_skill_ids: list[int]


async def to_profile_unit_info(
    context: idol.BasicSchoolIdolContext, unit_data: main.Unit, museum_param: museum.MuseumParameterData
):
    unit_info = await unit.get_unit_info(context, unit_data.unit_id)
    if unit_info is None:
        raise ValueError("unit_info is none")

    unit_full_data, unit_stats = await unit.get_unit_data_full_info(context, unit_data)
    # Calculate unit level
    unit_rarity = await unit.get_unit_rarity(context, unit_info.rarity)
    if unit_rarity is None:
        raise RuntimeError("unit_rarity is none")

    idolized = unit_data.rank == unit_info.rank_max
    real_max_exp = 0 if unit_stats.level == unit_rarity.before_level_max and not idolized else unit_stats.next_exp
    removable_skill_max = unit_data.unit_removable_skill_capacity == unit_info.max_removable_skill_capacity
    return ProfileUnitInfo(
        unit_owning_user_id=unit_data.id,
        unit_id=unit_data.unit_id,
        exp=unit_full_data.exp,
        next_exp=real_max_exp,
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
        total_smile=unit_stats.smile + museum_param.smile,
        total_cute=unit_stats.pure + museum_param.pure,
        total_cool=unit_stats.cool + museum_param.cool,
        total_hp=unit_full_data.max_hp,
        is_love_max=unit_full_data.is_love_max,
        is_level_max=unit_full_data.is_level_max,
        is_rank_max=unit_full_data.is_rank_max,
        is_signed=unit_data.is_signed,
        is_skill_level_max=unit_full_data.is_skill_level_max,
        is_removable_skill_capacity_max=removable_skill_max,
        removable_skill_ids=[],
        insert_date=util.timestamp_to_datetime(unit_data.insert_date),
    )
