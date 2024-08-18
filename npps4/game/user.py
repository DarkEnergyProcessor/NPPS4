import pydantic

from .. import idol
from .. import util
from ..system import advanced
from ..system import common
from ..system import unit
from ..system import user


class BirthdayUserInfoResponse(pydantic.BaseModel):
    birth_month: int
    birth_day: int


class UserInfoResponse(common.TimestampMixin):
    user: user.UserInfoData
    birth: BirthdayUserInfoResponse | None = None
    ad_status: bool | None = None


class ChangeNameRequest(pydantic.BaseModel):
    name: str


class ChangeNameResponse(pydantic.BaseModel):
    before_name: str
    after_name: str


class UserNavi(pydantic.BaseModel):
    user_id: int
    unit_owning_user_id: int


class UserGetNaviResponse(common.TimestampMixin):
    user: UserNavi


class UserNotificationTokenRequest(pydantic.BaseModel):
    notification_token: str


class UserChangeNaviRequest(pydantic.BaseModel):
    unit_owning_user_id: int


class UserSetBirthdayRequest(pydantic.BaseModel):
    birth_month: int
    birth_day: int


class UserAddUnitMaxRequest(pydantic.BaseModel):
    amount: int


class UserAddUnitResponse(pydantic.BaseModel):
    used_loveca: int
    after_unit_max: int


class UserSetNotificationNotification(pydantic.BaseModel):
    lp: bool
    live: bool
    push: bool
    lbonus: bool
    campaign: bool
    muse_event: bool
    update_info: bool
    aqours_event: bool
    muse_birthday: bool
    muse_secretbox: bool
    aqours_birthday: bool
    aqours_secretbox: bool


class UserSetNotificationRequest(pydantic.BaseModel):
    notification: UserSetNotificationNotification


@idol.register("user", "changeName", batchable=False)
async def user_changename(context: idol.SchoolIdolUserParams, request: ChangeNameRequest) -> ChangeNameResponse:
    await advanced.test_name(context, request.name)
    current_user = await user.get_current(context)
    oldname = current_user.name
    current_user.name = request.name
    return ChangeNameResponse(before_name=oldname, after_name=request.name)


@idol.register("user", "getNavi")
async def user_getnavi(context: idol.SchoolIdolUserParams) -> UserGetNaviResponse:
    current_user = await user.get_current(context)
    center = await unit.get_unit_center(context, current_user)
    return UserGetNaviResponse(
        user=UserNavi(user_id=current_user.id, unit_owning_user_id=center),
    )


@idol.register("user", "userInfo", exclude_none=True)
async def user_userinfo(context: idol.SchoolIdolUserParams) -> UserInfoResponse:
    u = await user.get_current(context)
    if u is None:
        raise idol.error.IdolError(idol.error.ERROR_CODE_LIB_ERROR, 500, "User is not known", http_code=500)
    return UserInfoResponse(
        user=await user.get_user_info(context, u),
        ad_status=False,
    )


@idol.register("user", "setNotificationToken", batchable=False)
async def user_setnotificationtoken(context: idol.SchoolIdolUserParams, request: UserNotificationTokenRequest) -> None:
    # TODO
    util.stub("user", "setNotificationToken", request)


@idol.register("user", "changeNavi")
async def user_changenavi(context: idol.SchoolIdolUserParams, request: UserChangeNaviRequest) -> None:
    current_user = await user.get_current(context)
    unit_data = await unit.get_unit(context, request.unit_owning_user_id)
    unit.validate_unit(current_user, unit_data)
    await unit.set_unit_center(context, current_user, unit_data)


@idol.register("user", "addUnitMax")
async def user_addunitmax(context: idol.SchoolIdolUserParams, request: UserAddUnitMaxRequest) -> UserAddUnitResponse:
    current_user = await user.get_current(context)
    current_loveca = user.get_loveca(current_user)
    if current_loveca < request.amount:
        raise idol.error.IdolError(detail="not enough loveca")

    # FIXME: Add limit
    user.sub_loveca(current_user, request.amount)
    current_user.unit_max = current_user.unit_max + request.amount * 4
    return UserAddUnitResponse(
        used_loveca=current_loveca - user.get_loveca(current_user), after_unit_max=current_user.unit_max
    )


async def user_setnotification(context: idol.SchoolIdolUserParams, request: UserSetNotificationRequest) -> None:
    # TODO
    util.stub("user", "setNotification", request)
