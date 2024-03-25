from .. import idol
from .. import util
from ..system import achievement
from ..system import advanced
from ..system import class_system as class_system_module
from ..system import museum
from ..system import reward
from ..system import scenario
from ..system import user

import pydantic


class ScenarioStartupRequest(pydantic.BaseModel):
    scenario_id: int


class ScenarioStatus(ScenarioStartupRequest):
    status: int


class ScenarioStatusResponse(pydantic.BaseModel):
    scenario_status_list: list[ScenarioStatus]


class ScenarioStartupResponse(ScenarioStartupRequest):
    scenario_adjustment: int = 50  # TODO where to get this value


class ScenarioRewardRequest(ScenarioStartupRequest):
    is_skipped: bool


class ScenarioRewardResponse(achievement.AchievementMixin):
    clear_scenario: ScenarioStartupRequest
    before_user_info: user.UserInfoData
    after_user_info: user.UserInfoData
    next_level_info: list[user.NextLevelInfo]
    unlock_random_live: bool = False  # TODO
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    new_achievement_cnt: int = 0
    museum_info: museum.MuseumInfoData
    server_timestamp: int = pydantic.Field(default_factory=util.time)
    present_cnt: int


@idol.register("scenario", "scenarioStatus")
async def scenario_scenariostatus(context: idol.SchoolIdolUserParams) -> ScenarioStatusResponse:
    current_user = await user.get_current(context)
    scenarios = await scenario.get_all(context, current_user)
    return ScenarioStatusResponse(
        scenario_status_list=[ScenarioStatus(scenario_id=sc.scenario_id, status=1 + sc.completed) for sc in scenarios]
    )


@idol.register("scenario", "startup")
async def scenario_startup(
    context: idol.SchoolIdolUserParams, request: ScenarioStartupRequest
) -> ScenarioStartupResponse:
    # Sanity check
    if not await scenario.valid(context, request.scenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SCENARIO_NOT_FOUND)

    # Sanity check #2
    current_user = await user.get_current(context)
    if not await scenario.is_unlocked(context, current_user, request.scenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SCENARIO_NOT_AVAILABLE)

    return ScenarioStartupResponse(scenario_id=request.scenario_id)


@idol.register("scenario", "reward")
async def scenario_reward(context: idol.SchoolIdolUserParams, request: ScenarioRewardRequest):
    # Sanity check
    if not await scenario.valid(context, request.scenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SCENARIO_NOT_FOUND)

    # Sanity check #2
    current_user = await user.get_current(context)
    if not await scenario.is_unlocked(context, current_user, request.scenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SCENARIO_NOT_AVAILABLE)
    if await scenario.is_completed(context, current_user, request.scenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SCENARIO_NO_REWARD)

    # Capture old user info
    old_user_info = await user.get_user_info(context, current_user)

    # Mark as complete
    await scenario.complete(context, current_user, request.scenario_id)

    # Trigger achievement
    finished_scenario_count = await scenario.count_completed(context, current_user)
    # FIXME: Recursive checking
    achievement_list = (
        await achievement.check_type_23(context, current_user, request.scenario_id)
        + await achievement.check_type_57(context, current_user, finished_scenario_count)
        + await achievement.check_type_53_recursive(context, current_user)
        + await achievement.check_type_30(context, current_user)
    )

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

    return ScenarioRewardResponse(
        clear_scenario=request,
        before_user_info=old_user_info,
        after_user_info=await user.get_user_info(context, current_user),
        next_level_info=await user.add_exp(context, current_user, 0),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
    )
