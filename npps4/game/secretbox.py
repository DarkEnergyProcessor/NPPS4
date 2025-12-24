import math

import pydantic

from .. import const
from .. import idol
from .. import util
from ..config import config
from ..system import achievement
from ..system import advanced
from ..system import common
from ..system import item
from ..system import museum
from ..system import reward
from ..system import secretbox
from ..system import secretbox_model
from ..system import unit
from ..system import unit_model
from ..system import user

from typing import Any


class SecretboxAllResponse(pydantic.BaseModel):
    use_cache: int
    is_unit_max: bool
    item_list: list[common.ItemCount]
    gauge_info: secretbox_model.SecretboxGaugeInfo = pydantic.Field(
        default_factory=secretbox_model.SecretboxGaugeInfo
    )  # TODO
    member_category_list: list[secretbox_model.SecretboxAllMemberCategory]


class SecretboxPonRequest(pydantic.BaseModel):
    id: int
    secret_box_id: int
    unit_type_ids: list  # TODO: list of what?


class SecretboxAddedGaugeInfo(secretbox_model.SecretboxGaugeInfo):
    added_gauge_point: int = 0


class SecretboxItems(pydantic.BaseModel):
    unit: list[unit_model.AnyUnitItem]
    item: list[common.AnyItem]


class SecretboxPonResponse(achievement.AchievementMixin, common.TimestampMixin, user.UserDiffMixin):
    is_unit_max: bool
    item_list: list[common.ItemCount]
    gauge_info: SecretboxAddedGaugeInfo = pydantic.Field(default_factory=SecretboxAddedGaugeInfo)  # TODO
    button_list: list[secretbox_model.AnySecretboxButton]
    secret_box_info: secretbox_model.AnySecretboxInfo
    secret_box_items: SecretboxItems
    secret_box_badge_flag: bool = False
    lowest_rarity: int = 1
    promotion_performance_rate: int = 0
    secret_box_parcel_type: int
    museum_info: museum.MuseumInfoData
    present_cnt: int


class SecretboxShowDetailRequest(pydantic.BaseModel):
    secret_box_id: int
    unit_type_id: int | None = None


class SecretboxShowDetailResponse(pydantic.BaseModel):
    unit_line_up: list[Any] = pydantic.Field(default_factory=list)
    url: str  # Scouting Rates URL
    rule_url: str  # Box scouting URL


USE_STUB_DATA = False

if USE_STUB_DATA:
    import json

    class CustomSecretBoxResponse(pydantic.BaseModel):
        use_cache: int
        is_unit_max: bool
        item_list: list[common.ItemCount]
        gauge_info: secretbox_model.SecretboxGaugeInfo = pydantic.Field(
            default_factory=secretbox_model.SecretboxGaugeInfo
        )
        member_category_list: list[dict[str, Any]]

    @idol.register("secretbox", "all")
    async def secretbox_all_stub(context: idol.SchoolIdolUserParams) -> CustomSecretBoxResponse:
        util.stub("secretbox", "all")
        with open("secretbox.json", "r", encoding="utf-8") as f:
            return CustomSecretBoxResponse(
                use_cache=1, is_unit_max=False, item_list=[], member_category_list=json.load(f)
            )

else:

    @idol.register("secretbox", "all")
    async def secretbox_all(context: idol.SchoolIdolUserParams) -> SecretboxAllResponse:
        current_user = await user.get_current(context)
        item_list = await item.get_item_list(context, current_user)
        return SecretboxAllResponse(
            use_cache=0,
            is_unit_max=await unit.is_unit_max(context, current_user),
            item_list=item_list[0],
            member_category_list=await secretbox.get_all_secretbox_data_response(context, current_user),
        )


HIDDEN_UR_UMI_RARE = False
LOWEST_RARITY_SORT_ORDER = (1, 2, 3, 5, 4)


@idol.register("secretbox", "pon", batchable=False)
@idol.register("secretbox", "multi", batchable=False)
async def secretbox_gachapon(context: idol.SchoolIdolUserParams, request: SecretboxPonRequest) -> SecretboxPonResponse:
    current_user = await user.get_current(context)
    secretbox_id, button_index, cost_index = secretbox.decode_cost_id(request.id)

    try:
        secretbox_data = secretbox.get_secretbox_data(secretbox_id)
    except KeyError as e:
        util.log("uh oh secretbox_data", secretbox_id, e=e)
        raise idol.error.by_code(idol.error.ERROR_CODE_SECRET_BOX_NOT_EXIST) from e

    try:
        secretbox_button = secretbox.get_secretbox_button(secretbox_data, button_index)
        secretbox_cost = secretbox_button.costs[cost_index - 1]
    except IndexError as e:
        util.log("uh oh secretbox_button", button_index, cost_index, e=e)
        raise idol.error.by_code(idol.error.ERROR_CODE_SECRET_BOX_COST_TYPE_IS_NOT_SPECIFIED) from e

    # Check currency
    cost_amount = math.ceil(secretbox_cost.cost_amount * config.CONFIG_DATA.gameplay.secretbox_cost_multiplier)
    if (
        await secretbox.get_user_currency(context, current_user, secretbox_cost.cost_type, secretbox_cost.cost_item_id)
        < cost_amount
    ):
        raise idol.error.by_code(idol.error.ERROR_CODE_SECRET_BOX_REMAINING_COST_IS_NOT_ENOUGH)

    # Capture current user info
    before_user_info = await user.get_user_info(context, current_user)

    # Roll units
    unit_roll = secretbox.roll_units(
        secretbox_id,
        secretbox_button.unit_count,
        guarantee_rarity=secretbox_button.guaranteed_rarity,
        guarantee_amount=secretbox_button.guarantee_specific_rarity_amount,
        rate_modifier=secretbox_button.rate_modifier,
    )
    unit_data_list: list[unit_model.AnyUnitItem] = []
    current_unit_count = await unit.count_units(context, current_user, True)

    umi_rare_mode = False
    lowest_rarity = 5  # sort order
    if HIDDEN_UR_UMI_RARE and len(unit_roll) == 1:
        unit_info = await unit.get_unit_info(context, unit_roll[0])
        if unit_info is not None and unit_info.rarity == 2 and unit_info.unit_type_id in (4, 94):
            umi_rare_mode = True

    unit_expiry = util.time() + const.COMMON_UNIT_EXPIRY
    for unit_id in unit_roll:
        reward_data = await unit.quick_create_by_unit_add(context, current_user, unit_id)
        assert reward_data.as_item_reward.unit_rarity_id is not None

        if not isinstance(reward_data.as_item_reward, unit_model.UnitItem):
            await unit.add_supporter_unit(context, current_user, reward_data.unit_id)
        else:
            if util.SYSRAND.randint(0, 1) == 1 and await unit.has_signed_variant(context, unit_id):
                reward_data.as_item_reward.is_signed = True

            if current_unit_count < current_user.unit_max:
                # Add directly
                assert reward_data.unit_data is not None
                assert reward_data.full_info is not None

                reward_data.unit_data.is_signed = reward_data.as_item_reward.is_signed

                await unit.add_unit_by_object(context, current_user, reward_data.unit_data)
                # Update unit_owning_user_id
                reward_data.update_unit_owning_user_id()
                current_unit_count = current_unit_count + 1
            else:
                # Move to present box
                unit_info = await unit.get_unit_info(context, reward_data.unit_id)
                assert unit_info is not None
                reward_data.as_item_reward.reward_box_flag = True
                await reward.add_item(
                    context,
                    current_user,
                    reward_data.as_item_reward,
                    "FIXME scouting JP Text",
                    "Scouting",
                    (unit_info.rarity <= 2 and unit_info.disable_rank_up == 0) * unit_expiry,
                )
        unit_data_list.append(reward_data.as_item_reward)
        lowest_rarity = min(lowest_rarity, LOWEST_RARITY_SORT_ORDER[reward_data.as_item_reward.unit_rarity_id - 1])

    # Trigger achievement
    achievement_list = await achievement.check(
        context,
        current_user,
        achievement.AchievementUpdateSecretbox(secretbox_id=secretbox_id, amount=secretbox_button.unit_count),
        achievement.AchievementUpdateNewUnit(),
        achievement.AchievementUpdateUnitRankUp(unit_ids=[]),
    )
    accomplished_rewards = [
        await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.accomplished
    ]
    unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.new]
    accomplished_rewards = await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
    unaccomplished_rewards = await advanced.fixup_achievement_reward(context, current_user, unaccomplished_rewards)
    await achievement.process_achievement_reward(
        context, current_user, achievement_list.accomplished, accomplished_rewards
    )

    # Subtract currency
    await secretbox.sub_user_currency(
        context, current_user, secretbox_cost.cost_type, secretbox_cost.cost_item_id, cost_amount
    )

    if umi_rare_mode:
        unit_data_list[0].unit_rarity_id = 4

    item_list = await item.get_item_list(context, current_user)

    return SecretboxPonResponse(
        before_user_info=before_user_info,
        after_user_info=await user.get_user_info(context, current_user),
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        is_unit_max=current_unit_count >= current_user.unit_max,
        item_list=item_list[0],
        button_list=await secretbox.get_secretbox_button_response(context, current_user, secretbox_data),
        secret_box_info=await secretbox.get_secretbox_info_response(
            context,
            current_user,
            secretbox_data,
            await secretbox.get_user_currency(
                context, current_user, secretbox_cost.cost_type, secretbox_cost.cost_item_id
            )
            >= cost_amount,
        ),
        secret_box_items=SecretboxItems(unit=unit_data_list, item=[]),
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=await reward.count_presentbox(context, current_user),
        promotion_performance_rate=100 if umi_rare_mode else 10,
        secret_box_parcel_type=secretbox_data.parcel_type,
        lowest_rarity=LOWEST_RARITY_SORT_ORDER[lowest_rarity - 1],
    )


@idol.register("secretbox", "showDetail")
async def secretbox_showdetail(
    context: idol.SchoolIdolUserParams, request: SecretboxShowDetailRequest
) -> SecretboxShowDetailResponse:
    util.stub("secretbox", "showDetail", context.raw_request_data)
    return SecretboxShowDetailResponse(
        # FIXME: Don't hardcode URLs
        # TODO: Make Member Filter in secretbox detail work.
        url=f"/webview.php/secretbox/detail?secretbox_id={request.secret_box_id}",
        rule_url="/something",
    )
