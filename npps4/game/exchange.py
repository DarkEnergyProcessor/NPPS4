import pydantic

from .. import const
from .. import idol
from .. import util
from ..system import advanced
from ..system import common
from ..system import exchange
from ..system import item_model
from ..system import reward
from ..system import user

STACKABLE_ITEMS = (
    const.ADD_TYPE.ITEM,
    const.ADD_TYPE.GAME_COIN,
    const.ADD_TYPE.LOVECA,
    const.ADD_TYPE.SOCIAL_POINT,
    const.ADD_TYPE.INVITE_POINT,
    const.ADD_TYPE.PLAYER_EXP,
    const.ADD_TYPE.UNIT_MAX,
    const.ADD_TYPE.EXCHANGE_POINT,
    const.ADD_TYPE.FRIEND_MAX,
    const.ADD_TYPE.WAITING_UNIT_MAX,
    const.ADD_TYPE.TRAINING_MAX,
    const.ADD_TYPE.SCHOOL_IDOL_SKILL,
    const.ADD_TYPE.EVENT_POINT,
    const.ADD_TYPE.LOTTERY_TICKET,
    const.ADD_TYPE.RECOVER_LP_ITEM,
    const.ADD_TYPE.TRADE_CAPITAL,
)


class ExchangePointResponse(pydantic.BaseModel):
    exchange_point_list: list[exchange.ExchangePointInfo]


class ExchangeItemInfoResponse(ExchangePointResponse):
    exchange_item_info: list[pydantic.SerializeAsAny[exchange.ExchangeItemBase]]


class ExchangeUsePointRequest(pydantic.BaseModel):
    exchange_item_id: int
    """Internal exchange item ID (automatically provided by NPPS4)."""

    rarity: int
    """Currency rarity used to perform exchange."""

    amount: int
    """How many to exchange?"""


class ExchangeUsePointResponse(common.TimestampMixin, user.UserDiffMixin):
    exchange_reward: list[pydantic.SerializeAsAny[item_model.Item]]
    """List of items given."""
    present_cnt: int
    """Amount of items in present box."""


@idol.register("exchange", "owningPoint")
async def exchange_owningpoint(context: idol.SchoolIdolUserParams) -> ExchangePointResponse:
    return ExchangePointResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context))
    )


@idol.register("exchange", "itemInfo")
async def exchange_iteminfo(context: idol.SchoolIdolUserParams) -> ExchangeItemInfoResponse:
    current_user = await user.get_current(context)
    return ExchangeItemInfoResponse(
        exchange_point_list=await exchange.get_exchange_points_response(context, await user.get_current(context)),
        exchange_item_info=await exchange.get_exchange_item_info(context, current_user),
    )


@idol.register("exchange", "usePoint")
async def exchange_usepoint(
    context: idol.SchoolIdolUserParams, request: ExchangeUsePointRequest
) -> ExchangeUsePointResponse:
    current_user = await user.get_current(context)
    raw_exchange_info = await exchange.find_raw_exchange_item_info_by_id(context, request.exchange_item_id)
    time = util.time()

    # Checks
    if request.amount <= 0:
        raise idol.error.IdolError(detail="Invalid amount")
    if raw_exchange_info is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_EXCHANGE_INVALID)
    if raw_exchange_info.end_time != 0 and time > raw_exchange_info.end_time:
        raise idol.error.by_code(idol.error.ERROR_CODE_EXCHANGE_ITEM_OUT_OF_DATE)

    exchange_info = await exchange.get_exchange_item_info_by_raw_info(context, current_user, raw_exchange_info, time)
    if (
        isinstance(exchange_info, (exchange.ExchangeItemWithMaxCount, exchange.ExchangeItemWithMaxCountAndExpiry))
        and (exchange_info.got_item_count + request.amount) > exchange_info.max_item_count
    ):
        raise idol.error.by_code(idol.error.ERROR_CODE_OVER_ADD_EXCHANGE_ITEM_COUNT_MAX_LIMIT)

    exchange_rarity = None
    for rarity in raw_exchange_info.costs:
        if rarity.rarity == request.rarity:
            exchange_rarity = rarity
            break
    if exchange_rarity is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_NOT_ENOUGH_EXCHANGE_POINT)

    required_exchange_point = exchange_rarity.cost * request.amount
    current_exchange_point = await exchange.get_exchange_point_amount(context, current_user, request.rarity)
    if current_exchange_point < required_exchange_point:
        raise idol.error.by_code(idol.error.ERROR_CODE_NOT_ENOUGH_EXCHANGE_POINT)

    # Specific case for background and award
    if raw_exchange_info.add_type in (const.ADD_TYPE.AWARD, const.ADD_TYPE.BACKGROUND):
        if await reward.has_at_least_one(context, current_user, raw_exchange_info.add_type, raw_exchange_info.item_id):
            errcode = (
                idol.error.ERROR_CODE_AWARD_IS_CONTAINED_IN_BOX
                if raw_exchange_info.add_type == const.ADD_TYPE.AWARD
                else idol.error.ERROR_CODE_BACKGROUND_IS_CONTAINED_IN_BOX
            )
            raise idol.error.by_code(errcode)

    # Capture old user info
    before_user_info = await user.get_user_info(context, current_user)

    # Perform the exchange
    item_result: list[pydantic.SerializeAsAny[item_model.Item]] = []
    if raw_exchange_info.add_type in STACKABLE_ITEMS:
        item_data_copy = item_model.BaseItem(
            add_type=raw_exchange_info.add_type,
            item_id=raw_exchange_info.item_id,
            amount=raw_exchange_info.amount * request.amount,
            extra_data=raw_exchange_info.extra_data,
        )
        item_data = await advanced.deserialize_item_data(context, item_data_copy)
        item_data.reward_box_flag = True
        await reward.add_item(context, current_user, item_data, "Sticker Shop")
        item_result.append(item_data)
    else:
        for _ in range(request.amount):
            item_data = await advanced.deserialize_item_data(context, raw_exchange_info)
            item_data.reward_box_flag = True
            await reward.add_item(context, current_user, item_data, "Sticker Shop")
            item_result.append(item_data)

    await exchange.sub_exchange_point(context, current_user, exchange_rarity.rarity, required_exchange_point)
    await exchange.add_exchange_item_got_count(context, current_user, exchange_info.exchange_item_id, request.amount)

    return ExchangeUsePointResponse(
        before_user_info=before_user_info,
        after_user_info=await user.get_user_info(context, current_user),
        exchange_reward=item_result,
        present_cnt=await reward.count_presentbox(context, current_user),
    )
