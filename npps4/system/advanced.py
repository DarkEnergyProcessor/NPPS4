import collections.abc
import dataclasses

import pydantic
import sqlalchemy

from . import award
from . import background
from . import common
from . import exchange
from . import item
from . import item_model
from . import live
from . import live_model
from . import museum
from . import scenario
from . import scenario_model
from . import unit
from . import unit_model
from .. import const
from .. import db
from .. import idol
from .. import leader_skill
from .. import util
from ..config import config
from ..db import game_mater
from ..db import main

from typing import Callable, cast, overload


# TODO: Replace with simple boolean.
@dataclasses.dataclass
class AddResult:
    success: bool

    def __bool__(self):
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


class LiveDeckUnitAttribute(common.CenterUnitInfo):
    unit_skill_level: int
    position: int


class LiveDeckStats(pydantic.BaseModel):
    smile: int = 0
    cute: int = 0
    cool: int = 0
    hp: int = 0


class LiveDeckInfo(pydantic.BaseModel):
    unit_deck_id: int
    total_smile: int
    total_cute: int
    total_cool: int
    total_hp: int
    prepared_hp_damage: int = 0
    total_status: LiveDeckStats
    center_bonus: LiveDeckStats
    si_bonus: LiveDeckStats
    unit_list: list[LiveDeckUnitAttribute]


async def add_item(context: idol.BasicSchoolIdolContext, user: main.User, i: common.AnyItem):
    match i.add_type:
        case const.ADD_TYPE.ITEM:
            match i.item_id:
                case 2:
                    user.social_point = user.social_point + i.amount
                    return AddResult(True)
                case 3:
                    user.game_coin = user.game_coin + i.amount
                    return AddResult(True)
                case 4:
                    user.free_sns_coin = user.free_sns_coin + i.amount
                    return AddResult(True)
                case _:
                    await item.add_item(context, user, i.item_id, i.amount)
                    return AddResult(True)
        case const.ADD_TYPE.UNIT:
            if await unit.is_support_member(context, i.item_id):
                return AddResult(await unit.add_supporter_unit(context, user, i.item_id, i.amount))
            else:
                unit_cnt = await unit.count_units(context, user, True)
                if (unit_cnt + i.amount) < user.unit_max:
                    assert type(i) is not unit_model.UnitSupportItem

                    for _ in range(i.amount):
                        if isinstance(i, unit_model.UnitItem):
                            unit_item = i
                        else:
                            unit_item = await unit.create_unit_item(context, i.item_id)
                            assert isinstance(unit_item, unit_model.UnitItem)

                        unit_data = await unit.create_unit_data(context, user, unit_item, True)
                        await unit.add_unit_by_object(context, user, unit_data)

                        unit_item.unit_owning_user_id = unit_data.id
                        if not isinstance(i, unit_model.UnitItem):
                            util.copy_attr(unit_item, i)

                    return AddResult(True)
                else:
                    return AddResult(False)
        case const.ADD_TYPE.GAME_COIN:
            user.game_coin = user.game_coin + i.amount
            return AddResult(True)
        case const.ADD_TYPE.LOVECA:
            if i.item_id == 1:
                user.paid_sns_coin = user.paid_sns_coin + i.amount
            else:
                user.free_sns_coin = user.free_sns_coin + i.amount
            return AddResult(True)
        case const.ADD_TYPE.SOCIAL_POINT:
            user.social_point = user.social_point + i.amount
            return AddResult(True)
        case const.ADD_TYPE.EXCHANGE_POINT:
            return AddResult(await exchange.add_exchange_point(context, user, i.item_id, i.amount))
        case const.ADD_TYPE.UNIT_MAX:
            # TODO: Limit max units
            user.unit_max = user.unit_max + i.amount
            return AddResult(True)
        # FIXME: Actually check for their return values of these unlocks.
        case const.ADD_TYPE.LIVE:
            live_item = cast(live_model.LiveItem, i)
            success = await live.unlock_normal_live(context, user, i.item_id)
            if success:
                live_item.additional_normal_live_status_list = await live.get_normal_live_clear_status_of_track(
                    context, user, i.item_id
                )
                live_item.additional_training_live_status_list = await live.get_training_live_clear_status_of_track(
                    context, user, i.item_id
                )
            return AddResult(success)
        case const.ADD_TYPE.AWARD:
            return AddResult(await award.unlock_award(context, user, i.item_id))
        case const.ADD_TYPE.BACKGROUND:
            return AddResult(await background.unlock_background(context, user, i.item_id))
        case const.ADD_TYPE.SCENARIO:
            return AddResult(await scenario.unlock(context, user, i.item_id))
        case const.ADD_TYPE.SCHOOL_IDOL_SKILL:
            await unit.add_unit_removable_skill(context, user, i.item_id, i.amount)
            return AddResult(True)
        case const.ADD_TYPE.RECOVER_LP_ITEM:
            await item.add_recovery_item(context, user, i.item_id, i.amount)
            return AddResult(True)
        case const.ADD_TYPE.MUSEUM:
            return AddResult(await museum.unlock(context, user, i.item_id))
    return AddResult(False)  # TODO


async def get_user_guest_party_info(context: idol.BasicSchoolIdolContext, user: main.User) -> PartyInfo:
    party_user_info = PartyUserInfo(user_id=user.id, name=user.name, level=user.level)

    # Get unit center info
    unit_center = await unit.get_unit_center(context, user)
    if unit_center is None:
        raise ValueError("invalid user no center")

    unit_data = await unit.get_unit(context, unit_center)
    unit.validate_unit(user, unit_data)
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


async def get_random_user_for_partylist(
    context: idol.BasicSchoolIdolContext, /, user: main.User, *, include_current: bool = True, limit: int = 3
):
    q = (
        sqlalchemy.select(main.User)
        .where(main.User.tutorial_state == -1, main.User.id != user.id)
        .order_by(sqlalchemy.func.random())
        .limit(limit)
    )
    result = await context.db.main.execute(q)
    userlist = list(result.scalars())
    if include_current:
        userlist.insert(0, user)
    return userlist


async def test_name(context: idol.BasicSchoolIdolContext, name: str):
    if name.isspace():
        raise idol.error.by_code(idol.error.ERROR_CODE_ONLY_WHITESPACE_CHARACTERS)
    if any(ord(c) < 32 for c in name):
        raise idol.error.by_code(idol.error.ERROR_CODE_UNAVAILABLE_WORDS)
    if await config.contains_badwords(name, context):
        raise idol.error.by_code(idol.error.ERROR_CODE_NG_WORDS)


_ACHIEVEMENT_REWARD_REPLACE_CRITERIA: dict[
    int, Callable[[idol.BasicSchoolIdolContext, main.User, int], collections.abc.Awaitable[bool]]
] = {
    const.ADD_TYPE.LIVE: live.has_normal_live_unlock,
    const.ADD_TYPE.AWARD: award.has_award,
    const.ADD_TYPE.BACKGROUND: background.has_background,
    const.ADD_TYPE.SCENARIO: scenario.is_unlocked,
    const.ADD_TYPE.MUSEUM: museum.has,
}


# Certain reward can only be given once. This function replaces them to give 1 loveca instead.
async def fixup_achievement_reward(
    context: idol.BasicSchoolIdolContext, user: main.User, rewardss: list[list[common.AnyItem]]
):
    result: list[list[common.AnyItem]] = []

    for reward_list in rewardss:
        new_reward_list: list[common.AnyItem] = []

        for ach_reward in reward_list:
            if (
                ach_reward.add_type in _ACHIEVEMENT_REWARD_REPLACE_CRITERIA
                and await _ACHIEVEMENT_REWARD_REPLACE_CRITERIA[ach_reward.add_type](context, user, ach_reward.item_id)
            ):
                new_reward_list.append(item.loveca(1))
            else:
                new_reward_list.append(ach_reward)

        result.append(new_reward_list)

    return result


class TeamStatCalculator:
    def __init__(self, context: idol.BasicSchoolIdolContext):
        self.context = context
        self.cached_unit_info: dict[int, unit.unit.Unit] = {}
        self.cached_unit_rarity: dict[int, unit.unit.Rarity] = {}
        self.cached_unit_leader_skill: dict[int, unit.unit.LeaderSkill] = {}
        self.cached_extra_unit_leader_skill: dict[int, unit.unit.ExtraLeaderSkill | None] = {}
        self.cached_unit_tags: dict[tuple[int, int], bool] = {}

    async def get_live_stats(
        self,
        unit_deck_id: int,
        player_units: list[main.Unit],
        guest: main.Unit,
        museum_param: museum.MuseumParameterData,
    ):
        # A few references:
        # https://github.com/NonSpicyBurrito/sif-team-simulator/blob/2b018170b509f93c0bff4f8f56e6cebd07c7f7fc/src/core/stats.ts
        # https://web.archive.org/web/20181212085822/http://decaf.kouhi.me/lovelive/index.php?title=Scoring
        # Note that the rest are trial-and-error, but it's assured that this method is exactly same as in calculated
        # score by the client.
        unit_infos: list[unit.unit.Unit] = []
        base_stats: list[unit.UnitStatsResult] = []
        love_stats: list[tuple[int, int, int]] = []
        sis_stats: list[tuple[int, int, int]] = []
        unit_types: list[int] = []

        total = LiveDeckStats()
        leader = LiveDeckStats()
        sis = LiveDeckStats()
        sis_ids: list[list[int]] = []
        unit_full: list[unit_model.UnitInfoData] = []

        # Retrieve base stats
        for unit_data in player_units:
            unit_info = await self.get_unit_info(unit_data.unit_id)
            unit_infos.append(unit_info)
            unit_types.append(unit_info.unit_type_id)

            unit_full_data, stats = await unit.get_unit_data_full_info(self.context, unit_data)
            unit_full.append(unit_full_data)
            sis_ids.append(await unit.get_unit_removable_skills(self.context, unit_data))
            base_stats.append(stats)
            total.hp = total.hp + stats.hp

        # Apply bond stat
        for i in range(9):
            unit_info = unit_infos[i]
            stats_info = base_stats[i]
            smile = stats_info.smile + museum_param.smile
            pure = stats_info.pure + museum_param.pure
            cool = stats_info.cool + museum_param.cool
            love = player_units[i].love
            match unit_info.attribute_id:
                case 1:
                    smile = smile + love
                case 2:
                    pure = pure + love
                case 3:
                    cool = cool + love

            love_stats.append((smile, pure, cool))

        # TODO: Apply SIS stats
        # TODO: Re-evaluate bond-SIS order with museum
        for stats in love_stats:
            sis_stats.append(stats)

        # Calculate leader bonus
        leader_stats = await self.calculate_leader_bonus(sis_stats, unit_types, player_units[4])
        guest_stats = await self.calculate_leader_bonus(sis_stats, unit_types, guest)

        final_stats: list[LiveDeckUnitAttribute] = []

        for i in range(9):
            sis.smile = sis.smile + sis_stats[i][0]
            sis.cute = sis.cute + sis_stats[i][1]
            sis.cool = sis.cool + sis_stats[i][2]
            leader.smile = leader.smile + leader_stats[i][0]
            leader.cute = leader.cute + leader_stats[i][1]
            leader.cool = leader.cool + leader_stats[i][2]

            current_smile = sis_stats[i][0] + leader_stats[i][0] + guest_stats[i][0]
            current_pure = sis_stats[i][1] + leader_stats[i][1] + guest_stats[i][1]
            current_cool = sis_stats[i][2] + leader_stats[i][2] + guest_stats[i][2]
            total.smile = total.smile + current_smile
            total.cute = total.cute + current_pure
            total.cool = total.cool + current_cool

            unit_data = player_units[i]
            unit_full_data = unit_full[i]
            final_stats.append(
                LiveDeckUnitAttribute(
                    unit_id=unit_data.unit_id,
                    level=unit_full_data.level,
                    love=unit_data.love,
                    rank=unit_data.rank,
                    display_rank=unit_data.display_rank,
                    smile=current_smile,
                    cute=current_pure,
                    cool=current_cool,
                    is_love_max=unit_full_data.is_love_max,
                    is_rank_max=unit_full_data.is_rank_max,
                    is_level_max=unit_full_data.is_level_max,
                    unit_skill_exp=unit_data.skill_exp,
                    unit_skill_level=unit_full_data.unit_skill_level,
                    unit_removable_skill_capacity=unit_data.unit_removable_skill_capacity,
                    removable_skill_ids=sis_ids[i],
                    position=i + 1,
                )
            )

        return LiveDeckInfo(
            unit_deck_id=unit_deck_id,
            total_smile=total.smile,
            total_cute=total.cute,
            total_cool=total.cool,
            total_hp=total.hp,
            total_status=total,
            center_bonus=leader,
            si_bonus=sis,
            unit_list=final_stats,
        )

    async def calculate_leader_bonus(
        self, stats: list[tuple[int, int, int]], unit_type_ids: list[int], leader_unit: main.Unit
    ):
        if len(stats) != len(unit_type_ids):
            raise ValueError("stats and unit_type_ids are different")
        result: list[tuple[int, int, int]] = [(0, 0, 0)] * len(stats)
        center = await self.get_unit_info(leader_unit.unit_id)

        if center.default_leader_skill_id:
            leader_skill_data = await self.get_unit_leader_skill(center.default_leader_skill_id)

            # Apply leader skill
            for i in range(len(stats)):
                result[i] = leader_skill.calculate_bonus(
                    leader_skill_data.leader_skill_effect_type, leader_skill_data.effect_value, *stats[i]
                )

            extra_leader_skill = await self.get_unit_extra_leader_skill(center.default_leader_skill_id)
            if extra_leader_skill is not None:
                # Apply extra leader skill
                for i in range(len(stats)):
                    if await self.has_member_tag(unit_type_ids[i], extra_leader_skill.member_tag_id):
                        bonus_stats = leader_skill.calculate_bonus(
                            extra_leader_skill.leader_skill_effect_type, extra_leader_skill.effect_value, *stats[i]
                        )
                    else:
                        bonus_stats = (0, 0, 0)

                    old_stats = result[i]
                    result[i] = (
                        old_stats[0] + bonus_stats[0],
                        old_stats[1] + bonus_stats[1],
                        old_stats[2] + bonus_stats[2],
                    )

        return result

    async def get_unit_info(self, unit_id: int):
        unit_info = await unit.get_unit_info(self.context, unit_id)
        if unit_info is None:
            raise ValueError("invalid unit_id (info is None)")
        return unit_info

    async def get_unit_rarity(self, rarity: int):
        unit_rarity = await unit.get_unit_rarity(self.context, rarity)
        if unit_rarity is None:
            raise ValueError("invalid rarity (unit_rarity is None)")
        return unit_rarity

    async def get_unit_leader_skill(self, leader_skill: int):
        unit_leader_skill = await unit.get_leader_skill(self.context, leader_skill)
        if unit_leader_skill is None:
            raise ValueError("invalid leader_skill (unit_leader_skill is None)")
        return unit_leader_skill

    async def get_unit_extra_leader_skill(self, leader_skill: int):
        return await unit.get_extra_leader_skill(self.context, leader_skill)

    async def has_member_tag(self, unit_type_id: int, member_tag_id: int):
        return await unit.unit_type_has_tag(self.context, (unit_type_id, member_tag_id))


@overload
async def get_item_name(context: idol.BasicSchoolIdolContext, item_data: item_model.Item, /) -> str: ...
@overload
async def get_item_name(context: idol.BasicSchoolIdolContext, add_type: const.ADD_TYPE, item_id: int, /) -> str: ...


async def get_item_name(
    context: idol.BasicSchoolIdolContext, add_type: const.ADD_TYPE | item_model.Item, item_id: int | None = None, /
) -> str:
    if isinstance(add_type, item_model.Item):
        return await get_item_name(context, add_type.add_type, add_type.item_id)

    if item_id is None:
        raise TypeError("expected item id")

    match add_type:
        case const.ADD_TYPE.NONE:
            return "None"
        case const.ADD_TYPE.ITEM:
            # Query kg_item_m
            item_info = await db.get_decrypted_row(context.db.item, item.item.KGItem, item_id)
            if item_info is not None:
                return context.get_text(item_info.name, item_info.name_en) or f"Unknown Item #{item_id}"
        case const.ADD_TYPE.UNIT:
            # Query unit info
            unit_info = await unit.get_unit_info(context, item_id)
            if unit_info is not None:
                eponym = context.get_text(unit_info.eponym, unit_info.eponym_en)
                unit_name = context.get_text(unit_info.name, unit_info.name_en)
                if eponym is None:
                    return f"#{unit_info.unit_number} - {unit_name}"
                else:
                    return f'#{unit_info.unit_number} - "{eponym}" {unit_name}'
        case const.ADD_TYPE.EXCHANGE_POINT:
            # Query stickers
            exchange_info = await db.get_decrypted_row(context.db.exchange, exchange.exchange.ExchangePoint, item_id)
            if exchange_info is not None:
                return context.get_text(exchange_info.name, exchange_info.name_en)
        case const.ADD_TYPE.LIVE:
            # Query live
            live_track_info = await live.get_live_track_info(context, item_id)
            if live_track_info is not None:
                live_name = context.get_text(live_track_info.name, live_track_info.name_en)
                return f"♪ {live_name} ♪"
        case const.ADD_TYPE.AWARD:
            # Query award_m
            award_info = await db.get_decrypted_row(context.db.item, item.item.Award, item_id)
            if award_info is not None:
                return context.get_text(award_info.name, award_info.name_en)
        case const.ADD_TYPE.BACKGROUND:
            # Query background_m
            bg_info = await db.get_decrypted_row(context.db.item, item.item.Background, item_id)
            if bg_info is not None:
                return context.get_text(bg_info.name, bg_info.name_en)
        case const.ADD_TYPE.SCENARIO:
            # Query scenario_m and scenario_chapter_m
            scenario_info = await db.get_decrypted_row(context.db.scenario, scenario.scenario.Scenario, item_id)
            if scenario_info is not None:
                scenario_chapter_info = await db.get_decrypted_row(
                    context.db.scenario, scenario.scenario.Chapter, scenario_info.scenario_chapter_id
                )
                if scenario_chapter_info is not None:
                    scenario_chapter_name = context.get_text(scenario_chapter_info.name, scenario_chapter_info.name_en)
                    scenario_name = context.get_text(scenario_info.title, scenario_info.title_en)
                    return f"{scenario_chapter_name} - {scenario_name}"
        case const.ADD_TYPE.SCHOOL_IDOL_SKILL:
            # Query unit_removable_skill_m
            unit_removable_skill_info = await unit.get_removable_skill_game_info(context, item_id)
            if unit_removable_skill_info is not None:
                return (
                    context.get_text(unit_removable_skill_info.name, unit_removable_skill_info.name_en)
                    or f"Unknown SIS #{item_id}"
                )
        case _:
            # Query add_type_m
            add_type_info = await context.db.game_mater.get(game_mater.AddType, int(add_type))
            if add_type_info is not None:
                return context.get_text(add_type_info.name, add_type_info.name_en)

    return f"Unknown (add_type {int(add_type)}, item_id {item_id})"


async def deserialize_item_data(
    context: idol.BasicSchoolIdolContext, item_base: item_model.BaseItem, /
) -> common.AnyItem:
    match item_base.add_type:
        case const.ADD_TYPE.UNIT:
            unit_extra_data = unit_model.UnitExtraData.EMPTY

            if item_base.extra_data:
                try:
                    unit_extra_data = unit_model.UnitExtraData.model_validate(item_base.extra_data)
                except pydantic.ValidationError:
                    pass

            item_data = await unit.create_unit_item(context, item_base.item_id, item_base.amount, unit_extra_data)
        case const.ADD_TYPE.SCENARIO:
            item_data = scenario_model.ScenarioItem(item_id=item_base.item_id, amount=item_base.amount)
        case const.ADD_TYPE.LIVE:
            item_data = live_model.LiveItem(item_id=item_base.item_id, amount=item_base.amount)
        case _:
            item_data = item_model.Item(add_type=item_base.add_type, item_id=item_base.item_id, amount=item_base.amount)
    item_data.item_category_id = await item.get_item_category(context, item_data)
    return item_data
