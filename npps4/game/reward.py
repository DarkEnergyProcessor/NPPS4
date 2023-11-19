import pydantic

from .. import idol
from .. import util

from ..idol.system import ad
from ..idol.system import class_system
from ..idol.system import item
from ..idol.system import museum
from ..idol.system import user

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


class RewardListResponse(pydantic.BaseModel):
    item_count: int
    limit: int = 20
    order: int
    items: list[IncentiveItem]
    ad_info: ad.AdInfo


class RewardListRequest(pydantic.BaseModel):
    # order values bitwise:
    # bit 0 - Set = ascending; Unset = descending.
    # bit 1 - Set = Display order by expiry. Unset = Display order by received.
    order: int
    # filter depends on the category:
    # 0. [unused]
    # 1. [rarity, attribute, show not in album?]
    # 2. [list of add types]
    filter: list[int]
    category: int  # 0 = All, 1 = Members, 2 = Items
    offset: int = 0


class RewardIncentiveItem(item.RewardWithCategory):
    incentive_id: int


class RewardOpenRequest(pydantic.BaseModel):
    incentive_id: int


class RewardOpenAllResponse(pydantic.BaseModel):
    reward_num: int
    opened_num: int
    total_num: int
    order: int
    upper_limit: bool
    reward_item_list: list[RewardIncentiveItem]
    before_user_info: user.UserInfoData
    after_user_info: user.UserInfoData
    class_system: class_system.ClassSystemData
    new_achievement_cnt: int
    museum_info: museum.MuseumInfoData
    server_timestamp: int
    present_cnt: int


class RewardHistoryRequest(pydantic.BaseModel):
    incentive_history_id: Any | None = None
    filter: list[int]
    category: int


class RewardHistoryResponse(pydantic.BaseModel):
    item_count: int
    limit: int = 20
    history: list[IncentiveItem]
    ad_info: ad.AdInfo


@idol.register("/reward/rewardList")
async def reward_rewardlist(context: idol.SchoolIdolUserParams, request: RewardListRequest) -> RewardListResponse:
    # TODO
    util.log(f"STUB /reward/rewardList {repr(request)}", severity=util.logging.WARNING)
    return RewardListResponse(item_count=0, order=request.order, items=[], ad_info=ad.AdInfo())


@idol.register("/reward/open")
async def reward_open(context: idol.SchoolIdolUserParams, request: RewardOpenRequest):
    # TODO
    util.log("STUB /reward/open", severity=util.logging.WARNING)
    return idol.core.DummyModel()


@idol.register("/reward/openAll")
async def reward_openall(context: idol.SchoolIdolUserParams, request: RewardListRequest) -> RewardOpenAllResponse:
    # TODO
    util.log("STUB /reward/openAll", severity=util.logging.WARNING)
    current_user = await user.get_current(context)
    user_info = await user.get_user_info(context, current_user)
    return RewardOpenAllResponse(
        reward_num=0,
        opened_num=0,
        total_num=0,
        order=request.order,
        upper_limit=False,
        reward_item_list=[],
        before_user_info=user_info,
        after_user_info=user_info,
        class_system=class_system.ClassSystemData(rank_info=class_system.ClassRankInfoData()),  # TODO
        new_achievement_cnt=0,
        museum_info=museum.MuseumInfoData(parameter=museum.MuseumParameterData(), contents_id_list=[]),  # TODO
        server_timestamp=util.time(),
        present_cnt=0,
    )


@idol.register("/reward/rewardHistory")
async def reward_rewardhistory(
    context: idol.SchoolIdolUserParams, request: RewardHistoryRequest
) -> RewardHistoryResponse:
    # TODO
    util.stub("reward", "rewardHistory", request)
    return RewardHistoryResponse(item_count=0, history=[], ad_info=ad.AdInfo())
