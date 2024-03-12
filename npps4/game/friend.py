import pydantic

from .. import idol
from .. import util
from ..system import unit
from ..system import unit_model
from ..system import user


class FriendListRequest(pydantic.BaseModel):
    type: int
    sort: int
    page: int


class FriendListResponse(pydantic.BaseModel):
    item_count: int
    friend_list: list
    new_friend_list: list
    server_timestamp: int = pydantic.Field(default_factory=util.time)


class FriendSearchRequest(pydantic.BaseModel):
    invite_code: str


class FriendSearchUserInfo(pydantic.BaseModel):
    user_id: int
    name: str
    level: int
    cost_max: int
    unit_max: int
    energy_max: int
    friend_max: int
    unit_cnt: int
    elapsed_time_from_login: str
    comment: str


class FriendSearchUnitInfo(unit_model.UnitInfoData):
    attribute: int
    smile: int
    cute: int
    cool: int
    setting_award_id: int
    removable_skill_ids: list[int]


class FriendSearchResponse(pydantic.BaseModel):
    user_info: FriendSearchUserInfo
    center_unit_info: FriendSearchUnitInfo
    setting_award_id: int
    is_alliance: bool
    friend_status: int
    server_timestamp: int = pydantic.Field(default_factory=util.time)


@idol.register("friend", "list")
async def friend_list(context: idol.SchoolIdolUserParams, request: FriendListRequest) -> FriendListResponse:
    # TODO
    util.stub("friend", "list", request)
    return FriendListResponse(item_count=0, friend_list=[], new_friend_list=[])


@idol.register("friend", "search")
async def friend_search(context: idol.SchoolIdolUserParams, request: FriendSearchRequest) -> FriendSearchResponse:
    current_user = await user.get_current(context)

    try:
        invite_code_int = int(request.invite_code)
    except ValueError:
        raise idol.error.by_code(idol.error.ERROR_CODE_FRIEND_USER_NOT_EXISTS) from None

    target_user = await user.find_by_invite_code(context, invite_code_int)

    if target_user is None or target_user.center_unit_owning_user_id == 0:
        raise idol.error.by_code(idol.error.ERROR_CODE_FRIEND_USER_NOT_EXISTS)

    unit_data = await unit.get_unit(context, target_user.center_unit_owning_user_id)
    unit_info = await unit.get_unit_info(context, unit_data.unit_id)
    assert unit_info is not None
    unit_data_full_info, unit_stats = await unit.get_unit_data_full_info(context, unit_data)

    return FriendSearchResponse(
        user_info=FriendSearchUserInfo(
            user_id=target_user.id,
            name=target_user.name,
            level=target_user.level,
            cost_max=((target_user.energy_max + target_user.over_max_energy) // 25)
            * 25,  # TODO get from game variables
            unit_max=target_user.unit_max,
            energy_max=target_user.energy_max,
            friend_max=target_user.friend_max,
            unit_cnt=await unit.count_units(context, target_user, True),
            elapsed_time_from_login="Unknown",
            comment=target_user.bio,
        ),
        center_unit_info=FriendSearchUnitInfo(
            unit_owning_user_id=unit_data_full_info.unit_owning_user_id,
            unit_id=unit_data_full_info.unit_id,
            exp=unit_data_full_info.exp,
            next_exp=unit_data_full_info.next_exp,
            level=unit_data_full_info.level,
            level_limit_id=unit_data_full_info.level_limit_id,
            max_level=unit_data_full_info.max_level,
            rank=unit_data_full_info.rank,
            max_rank=unit_data_full_info.max_rank,
            love=unit_data_full_info.love,
            max_love=unit_data_full_info.max_love,
            unit_skill_level=unit_data_full_info.unit_skill_level,
            skill_level=unit_data_full_info.unit_skill_level,
            max_hp=unit_data_full_info.max_hp,
            favorite_flag=unit_data_full_info.favorite_flag,
            display_rank=unit_data_full_info.display_rank,
            unit_skill_exp=unit_data_full_info.unit_skill_exp,
            unit_removable_skill_capacity=unit_data_full_info.unit_removable_skill_capacity,
            is_removable_skill_capacity_max=unit_data_full_info.is_removable_skill_capacity_max,
            is_love_max=unit_data_full_info.is_love_max,
            is_level_max=unit_data_full_info.is_level_max,
            is_rank_max=unit_data_full_info.is_rank_max,
            is_signed=unit_data_full_info.is_signed,
            is_skill_level_max=unit_data_full_info.is_skill_level_max,
            attribute=unit_info.attribute_id,
            smile=unit_stats.smile,
            cute=unit_stats.pure,
            cool=unit_stats.cool,
            setting_award_id=target_user.active_award,
            removable_skill_ids=await unit.get_unit_removable_skills(context, unit_data),
        ),
        setting_award_id=target_user.active_award,
        is_alliance=False,  # TODO
        friend_status=int(current_user.id == target_user.id),  # TODO
    )
