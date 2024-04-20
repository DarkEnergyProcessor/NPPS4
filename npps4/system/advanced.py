import dataclasses

import pydantic
import sqlalchemy

from . import achievement
from . import award
from . import background
from . import common
from . import exchange
from . import item
from . import item_model
from . import live
from . import live_model
from . import museum
from . import reward
from . import scenario
from . import unit
from . import unit_model
from .. import const
from .. import idol
from .. import leader_skill
from ..config import config
from ..db import main

from typing import Any, Awaitable, Callable, cast


@dataclasses.dataclass
class AddResult:
    success: bool
    reason_unit_full: bool = False
    extra_data: Any | None = None

    def __bool__(self):
        return self.success

    @property
    def unit_data(self) -> main.Unit:
        """Get underlying unit data (for unit addition only)"""
        if isinstance(self.extra_data, main.Unit):
            return self.extra_data
        raise TypeError("cannot get unit_data")


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
    prepared_hp_damage: int = 0
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
                if unit_cnt < user.unit_max:
                    unit_level = 1
                    if isinstance(i, unit_model.UnitItem):
                        unit_level = i.level
                    unit_data = await unit.add_unit(context, user, i.item_id, True, level=unit_level)
                    if isinstance(i, unit_model.UnitItem):
                        i.unit_owning_user_id = unit_data.id
                    return AddResult(True, extra_data=unit_data)
                else:
                    return AddResult(False, reason_unit_full=True)
        case const.ADD_TYPE.GAME_COIN:
            user.game_coin = user.game_coin + i.amount
            return AddResult(True)
        case const.ADD_TYPE.LOVECA:
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
            await live.unlock_normal_live(context, user, i.item_id)
            live_item.additional_normal_live_status_list = await live.get_normal_live_clear_status_of_track(
                context, user, i.item_id
            )
            return AddResult(True)
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
    unit_data = await unit.get_unit(context, await unit.get_unit_center(context, user))
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
        .where(main.User.tutorial_state == -1)
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
    int, Callable[[idol.BasicSchoolIdolContext, main.User, int], Awaitable[bool]]
] = {
    const.ADD_TYPE.LIVE: live.has_live_unlock,
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


async def give_achievement_reward(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    ach_info: achievement.achievement.Achievement,
    rewards: list[item_model.Item],
):
    for r in rewards:
        # TODO: Proper message for reward insertion
        if r.reward_box_flag:
            await reward.add_item(
                context,
                user,
                r,
                ach_info.title or "FIXME",
                ach_info.title_en or ach_info.title or "FIXME EN",
            )
        else:
            add_result = await add_item(context, user, r)
            if not add_result.success:
                await reward.add_item(
                    context,
                    user,
                    r,
                    ach_info.title or "FIXME",
                    ach_info.title_en or ach_info.title or "FIXME EN",
                )


async def process_achievement_reward(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    achievements: list[main.Achievement],
    rewardss: list[list[item_model.Item]],
):
    for ach, reward_list in zip(achievements, rewardss):
        ach_info = await achievement.get_achievement_info(context, ach.achievement_id)
        if ach_info is not None and ach_info.auto_reward_flag:
            await give_achievement_reward(context, user, ach_info, reward_list)
            await achievement.mark_achievement_reward_claimed(context, ach)
    await context.db.main.flush()


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
        max_hp = 0

        # Retrieve base stats
        for unit_data in player_units:
            unit_info = await self.get_unit_info(unit_data.unit_id)
            unit_infos.append(unit_info)
            unit_types.append(unit_info.unit_type_id)

            unit_rarity = await self.get_unit_rarity(unit_info.rarity)
            stats = await unit.get_unit_stats_from_unit_data(self.context, unit_data, unit_info, unit_rarity)
            base_stats.append(stats)
            max_hp = max_hp + stats.hp

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

        smile = 0
        pure = 0
        cool = 0

        final_stats: list[LiveDeckUnitAttribute] = []

        for i in range(9):
            current_smile = sis_stats[i][0] + leader_stats[i][0] + guest_stats[i][0]
            current_pure = sis_stats[i][1] + leader_stats[i][1] + guest_stats[i][1]
            current_cool = sis_stats[i][2] + leader_stats[i][2] + guest_stats[i][2]
            smile = smile + current_smile
            pure = pure + current_pure
            cool = cool + current_cool
            final_stats.append(LiveDeckUnitAttribute(smile=current_smile, cute=current_pure, cool=current_cool))

        return LiveDeckInfo(
            unit_deck_id=unit_deck_id,
            total_smile=smile,
            total_cute=pure,
            total_cool=cool,
            total_hp=max_hp,
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
        unit_info = self.cached_unit_info.get(unit_id)
        if unit_info is None:
            unit_info = await unit.get_unit_info(self.context, unit_id)
            if unit_info is None:
                raise ValueError("invalid unit_id (info is None)")
            self.cached_unit_info[unit_id] = unit_info
        return unit_info

    async def get_unit_rarity(self, rarity: int):
        unit_rarity = self.cached_unit_rarity.get(rarity)
        if unit_rarity is None:
            unit_rarity = await unit.get_unit_rarity(self.context, rarity)
            if unit_rarity is None:
                raise ValueError("invalid rarity (unit_rarity is None)")
            self.cached_unit_rarity[rarity] = unit_rarity
        return unit_rarity

    async def get_unit_leader_skill(self, leader_skill: int):
        unit_leader_skill = self.cached_unit_leader_skill.get(leader_skill)
        if unit_leader_skill is None:
            unit_leader_skill = await unit.get_leader_skill(self.context, leader_skill)
            if unit_leader_skill is None:
                raise ValueError("invalid leader_skill (unit_leader_skill is None)")
            self.cached_unit_leader_skill[leader_skill] = unit_leader_skill
        return unit_leader_skill

    async def get_unit_extra_leader_skill(self, leader_skill: int):
        if leader_skill not in self.cached_extra_unit_leader_skill:
            self.cached_extra_unit_leader_skill[leader_skill] = await unit.get_extra_leader_skill(
                self.context, leader_skill
            )
        return self.cached_extra_unit_leader_skill[leader_skill]

    async def has_member_tag(self, unit_type_id: int, member_tag_id: int):
        result = self.cached_unit_tags.get((unit_type_id, member_tag_id))
        if result is None:
            result = await unit.unit_type_has_tag(self.context, unit_type_id, member_tag_id)
            self.cached_unit_tags[(unit_type_id, member_tag_id)] = result

        return result
