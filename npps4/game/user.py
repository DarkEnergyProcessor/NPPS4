from .. import config
from .. import idol
from .. import util
from ..idol import error
from ..idol.system import core
from ..idol.system import unit
from ..idol.system import user

import pydantic


class UserInfoDataResponse(pydantic.BaseModel):
    user_id: int
    name: str
    level: int
    exp: int
    previous_exp: int
    next_exp: int
    game_coin: int
    sns_coin: int
    free_sns_coin: int
    paid_sns_coin: int
    social_point: int
    unit_max: int
    waiting_unit_max: int
    energy_max: int
    energy_full_time: str
    license_live_energy_recoverly_time: int
    energy_full_need_time: int
    over_max_energy: int
    training_energy: int
    training_energy_max: int
    friend_max: int
    invite_code: str
    insert_date: str
    update_date: str
    tutorial_state: int
    # TODO
    lp_recovery_item: list = []


class BirthdayUserInfoResponse(pydantic.BaseModel):
    birth_month: int
    birth_day: int


class UserInfoResponse(pydantic.BaseModel):
    user: UserInfoDataResponse
    birth: BirthdayUserInfoResponse | None = None
    ad_status: bool | None = None
    server_timestamp: int


class ChangeNameRequest(pydantic.BaseModel):
    name: str


class ChangeNameResponse(pydantic.BaseModel):
    before_name: str
    after_name: str


class UserNavi(pydantic.BaseModel):
    user_id: int
    unit_owning_user_id: int


class UserGetNaviResponse(pydantic.BaseModel):
    user: UserNavi
    server_timestamp: int


@idol.register("/user/changeName", batchable=False)
async def user_changename(context: idol.SchoolIdolUserParams, request: ChangeNameRequest) -> ChangeNameResponse:
    if config.contains_badwords(request.name):
        raise error.IdolError(error.ERROR_CODE_NG_WORDS)

    current_user = await user.get_current(context)
    oldname = current_user.name
    current_user.name = request.name
    return ChangeNameResponse(before_name=oldname, after_name=request.name)


@idol.register("/user/getNavi")
async def user_getnavi(context: idol.SchoolIdolUserParams) -> UserGetNaviResponse:
    current_user = await user.get_current(context)
    center = await unit.get_unit_center(context, current_user)
    return UserGetNaviResponse(
        user=UserNavi(user_id=context.token.user_id, unit_owning_user_id=center.unit_id if center is not None else 0),
        server_timestamp=util.time(),
    )


@idol.register("/user/userInfo", exclude_none=True)
async def user_userinfo(context: idol.SchoolIdolUserParams) -> UserInfoResponse:
    u = await user.get_current(context)
    if u is None:
        raise error.IdolError(error.ERROR_CODE_LIB_ERROR, 500, "User is not known", http_code=500)
    return UserInfoResponse(
        user=UserInfoDataResponse(
            user_id=u.id,
            name=u.name,
            level=u.level,
            exp=u.exp,
            previous_exp=core.get_next_exp_cumulative(u.level - 1),
            next_exp=core.get_next_exp_cumulative(u.level),
            game_coin=u.game_coin,
            sns_coin=u.free_sns_coin + u.paid_sns_coin,
            free_sns_coin=u.free_sns_coin,
            paid_sns_coin=u.paid_sns_coin,
            social_point=u.social_point,
            unit_max=u.unit_max,
            waiting_unit_max=u.waiting_unit_max,
            energy_max=u.energy_max,
            energy_full_time=util.timestamp_to_datetime(u.energy_full_time),
            license_live_energy_recoverly_time=u.license_live_energy_recoverly_time,
            energy_full_need_time=u.energy_full_need_time,
            over_max_energy=u.over_max_energy,
            training_energy=u.training_energy,
            training_energy_max=u.training_energy_max,
            friend_max=u.friend_max,
            invite_code=u.friend_id,
            insert_date=util.timestamp_to_datetime(u.insert_date),
            update_date=util.timestamp_to_datetime(u.update_date),
            tutorial_state=u.tutorial_state,
        ),
        ad_status=False,
        server_timestamp=util.time(),
    )
