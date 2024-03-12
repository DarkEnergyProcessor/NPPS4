from .. import const
from .. import idol
from .. import util
from ..system import class_system as class_system_module
from ..system import common
from ..system import item
from ..system import museum
from ..system import reward
from ..system import subscenario
from ..system import user

import pydantic


class SubScenarioStartupRequest(pydantic.BaseModel):
    subscenario_id: int


class SubScenarioStatus(SubScenarioStartupRequest):
    status: int


class SubScenarioStatusResponse(pydantic.BaseModel):
    subscenario_status_list: list[SubScenarioStatus]
    unlocked_subscenario_ids: list[int]


class SubScenarioStartupResponse(SubScenarioStartupRequest):
    scenario_adjustment: int = 50  # TODO where to get this value


class SubScenarioRewardRequest(SubScenarioStartupRequest):
    is_skipped: bool


class SubScenarioRewardResponse(pydantic.BaseModel):
    clear_subscenario: SubScenarioStartupRequest
    before_user_info: user.UserInfoData
    after_user_info: user.UserInfoData
    next_level_info: list[user.NextLevelInfo]
    base_reward_info: common.BaseRewardInfo
    item_reward_info: list[common.AnyItem]
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    new_achievement_cnt: int = 0
    museum_info: museum.MuseumInfoData
    server_timestamp: int = pydantic.Field(default_factory=util.time)
    present_cnt: int


@idol.register("subscenario", "subscenarioStatus")
async def subscenario_status(context: idol.SchoolIdolUserParams) -> SubScenarioStatusResponse:
    current_user = await user.get_current(context)
    subscenarios = await subscenario.get_all(context, current_user)
    return SubScenarioStatusResponse(
        subscenario_status_list=[
            SubScenarioStatus(subscenario_id=sc.subscenario_id, status=1 + sc.completed) for sc in subscenarios
        ],
        unlocked_subscenario_ids=[],
    )


@idol.register("subscenario", "startup")
async def subscenario_startup(
    context: idol.SchoolIdolUserParams, request: SubScenarioStartupRequest
) -> SubScenarioStartupResponse:
    # Sanity check
    if not await subscenario.valid(context, request.subscenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SUBSCENARIO_NOT_FOUND)

    # Sanity check #2
    current_user = await user.get_current(context)
    if not await subscenario.is_unlocked(context, current_user, request.subscenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SUBSCENARIO_NOT_AVAILABLE)

    return SubScenarioStartupResponse(subscenario_id=request.subscenario_id)


@idol.register("subscenario", "reward")
async def subscenario_reward(
    context: idol.SchoolIdolUserParams, request: SubScenarioRewardRequest
) -> SubScenarioRewardResponse:
    # Sanity check
    if not await subscenario.valid(context, request.subscenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SUBSCENARIO_NOT_FOUND)

    # Sanity check #2
    current_user = await user.get_current(context)
    if not await subscenario.is_unlocked(context, current_user, request.subscenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SUBSCENARIO_NOT_AVAILABLE)
    if await subscenario.is_completed(context, current_user, request.subscenario_id):
        raise idol.error.by_code(idol.error.ERROR_CODE_SUBSCENARIO_NO_REWARD)

    # Capture old user info
    old_user_info = await user.get_user_info(context, current_user)

    # Add G and loveca
    current_user.free_sns_coin = current_user.free_sns_coin + const.SUBSCENARIO_LOVECA_REWARD_AMOUNT
    current_user.game_coin = current_user.game_coin + const.SUBSCENARIO_GAME_COIN_REWARD_AMOUNT
    loveca_reward = item.loveca(const.SUBSCENARIO_LOVECA_REWARD_AMOUNT)
    loveca_reward.comment = (
        const.SUBSCENARIO_REWARD_COMMENT_JP if context.is_lang_jp() else const.SUBSCENARIO_REWARD_COMMENT_EN
    )

    # Mark as complete
    await subscenario.complete(context, current_user, request.subscenario_id)

    return SubScenarioRewardResponse(
        clear_subscenario=request,
        before_user_info=old_user_info,
        after_user_info=await user.get_user_info(context, current_user),
        next_level_info=await user.add_exp(context, current_user, 0),
        base_reward_info=common.BaseRewardInfo(
            game_coin=const.SUBSCENARIO_GAME_COIN_REWARD_AMOUNT, game_coin_reward_box_flag=False
        ),
        item_reward_info=[loveca_reward],
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
    )
