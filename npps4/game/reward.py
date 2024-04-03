import enum

import pydantic

from .. import idol
from .. import util

from ..system import ad_model
from ..system import class_system
from ..system import common
from ..system import item_model
from ..system import museum
from ..system import reward
from ..system import user

from typing import Any


class IncentiveItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    incentive_id: int
    incentive_item_id: int
    add_type: int
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


class RewardOpenAllResponse(common.TimestampMixin, user.UserDiffMixin):
    reward_num: int
    opened_num: int
    total_num: int
    order: int
    upper_limit: bool
    reward_item_list: list[pydantic.SerializeAsAny[RewardIncentiveItem]]
    class_system: class_system.ClassSystemData
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
                add_type=i.add_type,
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


# @idol.register("reward", "open")
async def reward_open(context: idol.SchoolIdolUserParams, request: RewardOpenRequest):
    # TODO
    util.stub("reward", "open", context.raw_request_data)
    return idol.core.DummyModel()


@idol.register("reward", "openAll")
async def reward_openall(context: idol.SchoolIdolUserParams, request: RewardListRequest) -> RewardOpenAllResponse:
    # TODO
    util.stub("reward", "openAll", context.raw_request_data)
    current_user = await user.get_current(context)
    user_info = await user.get_user_info(context, current_user)
    reward_count = min(await reward.count_presentbox(context, current_user), 1000)
    return RewardOpenAllResponse(
        reward_num=reward_count,
        opened_num=0,
        total_num=reward_count,
        order=request.order,
        upper_limit=False,
        reward_item_list=[],
        before_user_info=user_info,
        after_user_info=user_info,
        class_system=class_system.ClassSystemData(rank_info=class_system.ClassRankInfoData()),  # TODO
        new_achievement_cnt=0,
        museum_info=await museum.get_museum_info_data(context, current_user),
        present_cnt=0,
    )


@idol.register("reward", "rewardHistory")
async def reward_rewardhistory(
    context: idol.SchoolIdolUserParams, request: RewardHistoryRequest
) -> RewardHistoryResponse:
    # TODO
    util.stub("reward", "rewardHistory", request)
    return RewardHistoryResponse(item_count=0, history=[], ad_info=ad_model.AdInfo())
