from .. import idol
from .. import util
from ..idol.system import achievement
from ..idol.system import advanced
from ..idol.system import common
from ..idol.system import class_system as class_system_module
from ..idol.system import museum
from ..idol.system import reward
from ..idol.system import scenario
from ..idol.system import user

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
    base_reward_info: common.BaseRewardInfo
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
