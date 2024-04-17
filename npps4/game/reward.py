import enum

import pydantic

from .. import const
from .. import idol
from .. import util

from ..system import achievement
from ..system import album
from ..system import ad_model
from ..system import advanced
from ..system import class_system as class_system_module
from ..system import common
from ..system import item_model
from ..system import museum
from ..system import reward
from ..system import unit
from ..system import unit_model
from ..system import user

from typing import Any


class IncentiveItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    incentive_id: int
    incentive_item_id: int
    add_type: const.ADD_TYPE
    amount: int
    item_category_id: int
    incentive_message: str
    insert_date: str
    remaining_time: str
    item_option: str | None = None  # FIXME: What is this?


class RewardOrder(enum.IntFlag):
    ORDER_ASCENDING = enum.auto()
    BY_EXPIRE_DATE = enum.auto()


class RewardListResponse(pydantic.BaseModel):
    item_count: int
    limit: int = 20
    order: RewardOrder
    items: list[pydantic.SerializeAsAny[IncentiveItem]]
    ad_info: ad_model.AdInfo


class RewardListRequest(reward.FilterConfig):
    order: RewardOrder
    offset: int = 0


class RewardOpenRequest(pydantic.BaseModel):
    incentive_id: int


class RewardIncentiveItem(item_model.Item, RewardOpenRequest):
    model_config = pydantic.ConfigDict(extra="allow")


class RewardOpenResponse(achievement.AchievementMixin, user.UserDiffMixin, unit_model.SupporterListInfoResponse):
    opened_num: int
    success: list[pydantic.SerializeAsAny[RewardIncentiveItem]]
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    present_cnt: int


class RewardOpenAllResponse(achievement.AchievementMixin, common.TimestampMixin, user.UserDiffMixin):
    reward_num: int
    opened_num: int
    total_num: int
    order: int
    upper_limit: bool
    reward_item_list: list[pydantic.SerializeAsAny[RewardIncentiveItem]]
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    new_achievement_cnt: int
    museum_info: museum.MuseumInfoData
    present_cnt: int


class RewardHistoryRequest(reward.FilterConfig):
    incentive_history_id: Any | None = None


class RewardHistoryResponse(pydantic.BaseModel):
    item_count: int
    limit: int = 20
    history: list[IncentiveItem]
    ad_info: ad_model.AdInfo


@idol.register("reward", "rewardList")
async def reward_rewardlist(context: idol.SchoolIdolUserParams, request: RewardListRequest) -> RewardListResponse:
    current_user = await user.get_current(context)
    incentive = await reward.get_presentbox(
        context,
        current_user,
        request,
        request.offset,
        20,
        RewardOrder.ORDER_ASCENDING in request.order,
        RewardOrder.BY_EXPIRE_DATE in request.order,
    )

    return RewardListResponse(
        item_count=len(incentive),
        order=request.order,
        items=[
            IncentiveItem(
                incentive_id=i.id,
                incentive_item_id=i.item_id,
                add_type=const.ADD_TYPE(i.add_type),
                amount=i.amount,
                item_category_id=0,
                incentive_message=i.get_message(context.lang),
                insert_date=util.timestamp_to_datetime(i.insert_date),
                remaining_time="Forever" if i.expire_date == 0 else util.timestamp_to_datetime(i.expire_date),
            )
            for i in incentive
        ],
        ad_info=ad_model.AdInfo(),
    )


@idol.register("reward", "open")
async def reward_open(context: idol.SchoolIdolUserParams, request: RewardOpenRequest) -> RewardOpenResponse:
    # https://github.com/Salaron/alay/blob/master/src/modules/api/reward/open.ts
    current_user = await user.get_current(context)
    incentive = await reward.get_incentive(context, current_user, request.incentive_id)
    if incentive is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_INCENTIVE_NONE)

    before_user = await user.get_user_info(context, current_user)
    item_data = await reward.resolve_incentive(context, current_user, incentive)
    add_result = await advanced.add_item(context, current_user, item_data)
    supp_units = await unit.get_all_supporter_unit(context, current_user)
    success = bool(add_result)

    achievement_list = achievement.AchievementContext()
    if success:
        await reward.remove_incentive(context, incentive)
        if item_data.add_type == const.ADD_TYPE.UNIT:
            # Trigger achievement
            achievement_list = await album.trigger_achievement(
                context, current_user, obtained=True, idolized=True, max_love=True, max_level=True
            ) + await achievement.check_type_53_recursive(context, current_user)

    # Give achievement rewards
    accomplished_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.accomplished
    ]
    unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.new]
    await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
    await advanced.fixup_achievement_reward(context, current_user, unaccomplished_rewards)
    await advanced.process_achievement_reward(
        context, current_user, achievement_list.accomplished, accomplished_rewards
    )

    return RewardOpenResponse(
        unit_support_list=[unit_model.SupporterInfoResponse(unit_id=supp[0], amount=supp[1]) for supp in supp_units],
        before_user_info=before_user,
        after_user_info=await user.get_user_info(context, current_user),
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        opened_num=success,
        success=(
            [RewardIncentiveItem.model_validate({"incentive_id": request.incentive_id} | item_data.model_dump())]
            if success
            else []
        ),
        present_cnt=await reward.count_presentbox(context, current_user),
    )


@idol.register("reward", "openAll")
async def reward_openall(context: idol.SchoolIdolUserParams, request: RewardListRequest) -> RewardOpenAllResponse:
    current_user = await user.get_current(context)
    before_user = await user.get_user_info(context, current_user)
    incentives = await reward.get_presentbox(
        context,
        current_user,
        request,
        0,
        1000,
        RewardOrder.ORDER_ASCENDING in request.order,
        RewardOrder.BY_EXPIRE_DATE in request.order,
    )
    reward_count = len(incentives)
    reward_item_list: list[RewardIncentiveItem] = []
    need_check_unit_ach = False

    for incentive in incentives:
        item_data = await reward.resolve_incentive(context, current_user, incentive)
        add_result = await advanced.add_item(context, current_user, item_data)
        success = bool(add_result)

        if success:
            reward_item_list.append(
                RewardIncentiveItem.model_validate(item_data.model_dump() | {"incentive_id": incentive.id})
            )
            await reward.remove_incentive(context, incentive)
            if item_data.add_type == const.ADD_TYPE.UNIT:
                need_check_unit_ach = True

    achievement_list = achievement.AchievementContext()
    if need_check_unit_ach:
        # Trigger achievement
        achievement_list = await album.trigger_achievement(
            context, current_user, obtained=True, idolized=True, max_love=True, max_level=True
        ) + await achievement.check_type_53_recursive(context, current_user)
    # Give achievement rewards
    accomplished_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.accomplished
    ]
    unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.new]
    await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
    await advanced.fixup_achievement_reward(context, current_user, unaccomplished_rewards)
    await advanced.process_achievement_reward(
        context, current_user, achievement_list.accomplished, accomplished_rewards
    )

    return RewardOpenAllResponse(
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        reward_num=reward_count,
        opened_num=len(reward_item_list),
        total_num=reward_count,
        order=request.order,
        upper_limit=False,
        reward_item_list=reward_item_list,
        before_user_info=before_user,
        after_user_info=await user.get_user_info(context, current_user),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
    )


@idol.register("reward", "rewardHistory")
async def reward_rewardhistory(
    context: idol.SchoolIdolUserParams, request: RewardHistoryRequest
) -> RewardHistoryResponse:
    # TODO
    util.stub("reward", "rewardHistory", request)
    return RewardHistoryResponse(item_count=0, history=[], ad_info=ad_model.AdInfo())
