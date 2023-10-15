from .. import idol
from .. import util
from ..idol.system import unit
from ..idol.system import user

import pydantic


class RemovableSkillInfoResponse(pydantic.BaseModel):
    owning_info: list
    equipment_info: list


class SupporterInfoResponse(pydantic.BaseModel):
    unit_id: int
    amount: int


class SupporterListInfoResponse(pydantic.BaseModel):
    unit_support_list: list[SupporterInfoResponse]


class UnitAccessoryInfoResponse(pydantic.BaseModel):
    accessory_list: list
    wearing_info: list
    especial_create_flag: bool


class UnitDeckPositionInfoResponse(pydantic.BaseModel):
    position: int
    unit_owning_user_id: int


class UnitDeckInfoResponse(pydantic.BaseModel):
    unit_deck_id: int
    main_flag: bool
    deck_name: str
    unit_owning_user_ids: list[UnitDeckPositionInfoResponse]


class UnitInfoResponse(pydantic.BaseModel):
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


class UnitAllInfoResponse(pydantic.BaseModel):
    active: list[UnitInfoResponse]
    waiting: list[UnitInfoResponse]


@idol.register("/unit/accessoryAll")
async def unit_accessoryall(context: idol.SchoolIdolUserParams) -> UnitAccessoryInfoResponse:
    # TODO
    util.log("STUB /unit/accessoryAll", severity=util.logging.WARNING)
    return UnitAccessoryInfoResponse(accessory_list=[], wearing_info=[], especial_create_flag=False)


@idol.register("/unit/deckInfo")
async def unit_deckinfo(context: idol.SchoolIdolUserParams) -> list[UnitDeckInfoResponse]:
    current_user = await user.get_current(context)
    result: list[UnitDeckInfoResponse] = []

    for i in range(1, 19):
        decklist = await unit.load_unit_deck(context, current_user, i)

        if decklist is not None:
            deckpos: list[UnitDeckPositionInfoResponse] = []
            for j, unit_id in enumerate(decklist[1], 1):
                if unit_id > 0:
                    deckpos.append(UnitDeckPositionInfoResponse(position=j, unit_owning_user_id=unit_id))

            deckinfo = UnitDeckInfoResponse(
                unit_deck_id=i,
                main_flag=current_user.active_deck_index == i,
                deck_name=decklist[0].name,
                unit_owning_user_ids=deckpos,
            )
            result.append(deckinfo)

    return result


@idol.register("/unit/removableSkillInfo")
async def unit_removableskillinfo(context: idol.SchoolIdolUserParams) -> RemovableSkillInfoResponse:
    # TODO
    util.log("STUB /unit/removableSkillInfo", severity=util.logging.WARNING)
    return RemovableSkillInfoResponse(owning_info=[], equipment_info=[])


@idol.register("/unit/supporterAll")
async def unit_supporterall(context: idol.SchoolIdolUserParams) -> SupporterListInfoResponse:
    current_user = await user.get_current(context)
    units = await unit.get_all_supporter_unit(context, current_user)

    return SupporterListInfoResponse(
        unit_support_list=[SupporterInfoResponse(unit_id=supp[0], amount=supp[1]) for supp in units]
    )


@idol.register("/unit/unitAll")
async def unit_unitall(context: idol.SchoolIdolUserParams) -> UnitAllInfoResponse:
    current_user = await user.get_current(context)
    units = await unit.get_all_units(context, current_user)

    unit_result: dict[bool, list[UnitInfoResponse]] = {False: [], True: []}

    for unit_data in units:
        unit_info = await unit.get_unit_info(context, unit_data.unit_id)
        if unit_info is None:
            raise RuntimeError("unit_info is none")

        # Calculate unit level
        unit_rarity = await unit.get_unit_rarity(context, unit_info)
        if unit_rarity is None:
            raise RuntimeError("unit_rarity is none")

        levelup_pattern = await unit.get_unit_level_up_pattern(context, unit_info)
        stats = unit.calculate_unit_stats(unit_info, levelup_pattern, unit_data.exp)

        # Calculate unit skill level
        skill = await unit.get_unit_skill(context, unit_info)
        skill_levels = await unit.get_unit_skill_level_up_pattern(context, skill)
        skill_stats = unit.calculate_unit_skill_stats(skill, skill_levels, unit_data.skill_exp)

        idolized = unit_data.rank == unit_info.rank_max
        skill_max = skill is None or skill_stats[0] == skill.max_level

        max_level = unit_rarity.after_level_max if idolized else unit_rarity.before_level_max
        max_love = unit_rarity.after_love_max if idolized else unit_rarity.before_love_max
        real_max_exp = 0 if stats.level == unit_rarity.before_level_max and not idolized else stats.next_exp
        removable_skill_max = unit_data.unit_removable_skill_capacity == unit_info.max_removable_skill_capacity

        unit_serialized_data = UnitInfoResponse(
            unit_owning_user_id=unit_data.id,
            unit_id=unit_data.unit_id,
            exp=unit_data.exp,
            next_exp=real_max_exp,
            level=stats.level,
            max_level=max_level,
            level_limit_id=unit_data.level_limit_id,
            rank=unit_data.rank,
            max_rank=unit_info.rank_max,
            love=unit_data.love,
            max_love=max_love,
            unit_skill_exp=unit_data.skill_exp,
            unit_skill_level=skill_stats[0],
            max_hp=stats.hp,
            unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
            favorite_flag=unit_data.favorite_flag,
            display_rank=unit_data.display_rank,
            is_rank_max=idolized,
            is_love_max=unit_data.love >= unit_rarity.after_love_max,
            is_level_max=stats.level >= unit_rarity.after_level_max,
            is_signed=unit_data.is_signed,
            is_skill_level_max=skill_max,
            is_removable_skill_capacity_max=removable_skill_max,
            insert_date=util.timestamp_to_datetime(unit_data.insert_date),
        )
        unit_result[unit_data.active].append(unit_serialized_data)

    return UnitAllInfoResponse(active=unit_result[True], waiting=unit_result[False])
