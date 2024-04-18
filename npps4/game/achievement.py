import pydantic


from .. import idol
from .. import util
from ..system import achievement
from ..system import advanced
from ..system import common
from ..system import museum
from ..system import reward
from ..system import unit
from ..system import unit_model
from ..system import user


class AchievementUnaccomplishedFilter(pydantic.BaseModel):
    filter_category_id: int
    achievement_list: list[achievement.AchievementData]
    count: int
    is_last: bool = True


class AchievementUnaccomplishedResponse(pydantic.RootModel[list[AchievementUnaccomplishedFilter]]):
    pass


class AchievementRewardOpenRequest(pydantic.BaseModel):
    accomplish_id: int


class AchievementRewardOpenResponse(
    achievement.AchievementMixin, common.TimestampMixin, user.UserDiffMixin, unit_model.SupporterListInfoResponse
):
    reward_item_list: list[pydantic.SerializeAsAny[common.AnyItem]]
    unit_support_list: list[unit_model.SupporterInfoResponse]
    present_cnt: int


class AchievementRewardOpenAllResponse(AchievementRewardOpenResponse):
    is_last: bool
    opened_num: int


@idol.register("achievement", "unaccomplishList")
async def achievement_unaccomplishlist(context: idol.SchoolIdolUserParams) -> AchievementUnaccomplishedResponse:
    current_user = await user.get_current(context)
    filter_ids = await achievement.get_achievement_filter_ids(context)

    result: list[AchievementUnaccomplishedFilter] = []
    for fcat in filter_ids:
        unaccomplished = await achievement.get_unclaimed_achievements_by_filter_id(context, current_user, fcat)
        unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in unaccomplished]
        ach_list = await achievement.to_game_representation(context, unaccomplished, unaccomplished_rewards)
        result.append(
            AchievementUnaccomplishedFilter(filter_category_id=fcat, achievement_list=ach_list, count=len(ach_list))
        )

    return AchievementUnaccomplishedResponse.model_validate(result)


@idol.register("achievement", "initialAccomplishedList")
async def achievement_initialaccomplishlist(context: idol.SchoolIdolUserParams) -> AchievementUnaccomplishedResponse:
    current_user = await user.get_current(context)
    filter_ids = await achievement.get_achievement_filter_ids(context)

    result: list[AchievementUnaccomplishedFilter] = []
    for fcat in filter_ids:
        accomplished = await achievement.get_accomplished_achievements_by_filter_id(context, current_user, fcat)
        accomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in accomplished]
        accomplished_rewards = await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
        ach_list = await achievement.to_game_representation(context, accomplished, accomplished_rewards)
        result.append(
            AchievementUnaccomplishedFilter(filter_category_id=fcat, achievement_list=ach_list, count=len(ach_list))
        )

    return AchievementUnaccomplishedResponse.model_validate(result)


@idol.register("achievement", "rewardOpen")
async def achievement_rewardopen(
    context: idol.SchoolIdolUserParams, request: AchievementRewardOpenRequest
) -> AchievementRewardOpenResponse:
    current_user = await user.get_current(context)
    achievement_id = int(request.accomplish_id)
    ach = await achievement.get_achievement(context, current_user, achievement_id)
    ach_info = await achievement.get_achievement_info(context, ach.achievement_id)
    rewards = await achievement.get_achievement_rewards(context, ach)
    new_rewards = await advanced.fixup_achievement_reward(context, current_user, [rewards])
    rewards = new_rewards[0]

    before_user = await user.get_user_info(context, current_user)

    for reward_item in rewards:
        success = await advanced.add_item(context, current_user, reward_item)
        if not bool(success):
            reward_item.reward_box_flag = True
            fallback_name = f"Achievement #{ach.achievement_id}"
            await reward.add_item(
                context,
                current_user,
                reward_item,
                ach_info.title or fallback_name,
                ach_info.title_en or ach_info.title or fallback_name,
            )

    # Mark claimed
    ach.is_reward_claimed = True
    await context.db.main.flush()
    achievement_count = await achievement.get_achievement_count(context, current_user, False)

    return AchievementRewardOpenResponse(
        accomplished_achievement_list=[],
        unaccomplished_achievement_cnt=achievement_count,
        added_achievement_list=[],
        new_achievement_cnt=achievement_count,
        before_user_info=before_user,
        after_user_info=await user.get_user_info(context, current_user),
        reward_item_list=rewards,
        unit_support_list=await unit.get_unit_support_list_response(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
    )


@idol.register("achievement", "rewardOpenAll")
async def achievement_rewardopenall(context: idol.SchoolIdolUserParams) -> AchievementRewardOpenAllResponse:
    current_user = await user.get_current(context)
    achievements = await achievement.get_unclaimed_achievements(context, current_user, True)
    opened_count = 0
    reward_item_list: list[common.AnyItem] = []
    before_user = await user.get_user_info(context, current_user)

    for ach in achievements:
        ach_info = await achievement.get_achievement_info(context, ach.achievement_id)
        rewards = await achievement.get_achievement_rewards(context, ach)
        new_rewards = await advanced.fixup_achievement_reward(context, current_user, [rewards])

        for reward_item in new_rewards[0]:
            success = await advanced.add_item(context, current_user, reward_item)
            if not bool(success):
                reward_item.reward_box_flag = True
                fallback_name = f"Achievement #{ach.achievement_id}"
                await reward.add_item(
                    context,
                    current_user,
                    reward_item,
                    ach_info.title or fallback_name,
                    ach_info.title_en or ach_info.title or fallback_name,
                )
            reward_item_list.append(reward_item)

        ach.is_reward_claimed = True
        opened_count = opened_count + 1

    achievement_count = await achievement.get_achievement_count(context, current_user, False)
    return AchievementRewardOpenAllResponse(
        accomplished_achievement_list=[],
        unaccomplished_achievement_cnt=achievement_count,
        added_achievement_list=[],
        new_achievement_cnt=achievement_count,
        before_user_info=before_user,
        after_user_info=await user.get_user_info(context, current_user),
        reward_item_list=reward_item_list,
        unit_support_list=await unit.get_unit_support_list_response(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
        is_last=True,
        opened_num=opened_count,
    )
