import pydantic

from .. import idol
from .. import util
from ..idol.system import museum
from ..idol.system import profile
from ..idol.system import unit
from ..idol.system import user


class ProfileLiveCount(pydantic.BaseModel):
    difficulty: int
    clear_cnt: int


class ProfileCardRanking(pydantic.BaseModel):
    unit_id: int
    total_love: int
    rank: int
    sign_flag: bool


class ProfileRequest(pydantic.BaseModel):
    user_id: int


class ProfileUserInfo(pydantic.BaseModel):
    user_id: int
    name: str
    level: int
    cost_max: int = 100  # TODO
    unit_max: int
    energy_max: int
    friend_max: int
    unit_cnt: int
    invite_code: str
    elapsed_time_from_login: str = "unknown"  # TODO
    introduction: str


class ProfileInfoResponse(pydantic.BaseModel):
    user_info: ProfileUserInfo
    center_unit_info: profile.ProfileUnitInfo
    navi_unit_info: profile.ProfileUnitInfo
    is_alliance: bool
    friend_status: int = 0
    setting_award_id: int
    setting_background_id: int


class ProfileRegisterRequest(pydantic.BaseModel):
    introduction: str


@idol.register("profile", "liveCnt")
async def profile_livecount(context: idol.SchoolIdolUserParams, request: ProfileRequest) -> list[ProfileLiveCount]:
    util.stub("profile", "liveCnt", request)
    return [ProfileLiveCount(difficulty=i, clear_cnt=0) for i in (1, 2, 3, 4, 6)]


@idol.register("profile", "cardRanking")
async def profile_cardranking(context: idol.SchoolIdolUserParams, request: ProfileRequest) -> list[ProfileCardRanking]:
    util.stub("profile", "cardRanking", request)
    return []


@idol.register("profile", "profileInfo")
async def profile_profileinfo(context: idol.SchoolIdolUserParams, request: ProfileRequest) -> ProfileInfoResponse:
    target_user = await user.get(context, request.user_id)
    if target_user is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_USER_NOT_EXIST)

    partner_unit_owning_user_id = await unit.get_unit_center(context, target_user)
    if partner_unit_owning_user_id == 0:
        raise idol.error.by_code(idol.error.ERROR_CODE_USER_NOT_EXIST)
    partner_unit = await unit.get_unit(context, partner_unit_owning_user_id)
    unit.validate_unit(target_user, partner_unit)

    active_deck = await unit.load_unit_deck(context, target_user, target_user.active_deck_index)
    if active_deck is None:
        raise idol.error.by_code(idol.error.ERROR_CODE_USER_NOT_EXIST)

    center_unit = await unit.get_unit(context, active_deck[1][4])

    unit_count = await unit.count_units(context, target_user, True)
    museum_data = await museum.get_museum_info_data(context, target_user)

    return ProfileInfoResponse(
        user_info=ProfileUserInfo(
            user_id=request.user_id,
            name=target_user.name,
            level=target_user.level,
            unit_max=target_user.unit_max,
            energy_max=target_user.energy_max,
            friend_max=target_user.friend_max,
            unit_cnt=unit_count,
            invite_code=target_user.friend_id,
            introduction="Hello",  # TODO
        ),
        center_unit_info=await profile.to_profile_unit_info(context, center_unit, museum_data.parameter),
        navi_unit_info=await profile.to_profile_unit_info(context, partner_unit, museum_data.parameter),
        is_alliance=False,  # TODO
        friend_status=0,
        setting_award_id=target_user.active_award,
        setting_background_id=target_user.active_background,
    )


@idol.register("profile", "profileRegister")
async def profile_profileregister(
    context: idol.SchoolIdolUserParams, request: ProfileRegisterRequest
) -> idol.core.DummyModel:
    # TODO
    util.stub("profile", "profileRegister", request)
    raise idol.error.by_code(idol.error.ERROR_CODE_ONLY_WHITESPACE_CHARACTERS)
    return idol.core.DummyModel()
