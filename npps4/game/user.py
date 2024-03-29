from .. import idol
from .. import util
from ..idol import error
from ..system import advanced
from ..system import unit
from ..system import user

import pydantic


class BirthdayUserInfoResponse(pydantic.BaseModel):
    birth_month: int
    birth_day: int


class UserInfoResponse(pydantic.BaseModel):
    user: user.UserInfoData
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


class UserNotificationTokenRequest(pydantic.BaseModel):
    notification_token: str


class UserChangeNaviRequest(pydantic.BaseModel):
    unit_owning_user_id: int


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
        server_timestamp=util.time(),
    )


@idol.register("user", "userInfo", exclude_none=True)
async def user_userinfo(context: idol.SchoolIdolUserParams) -> UserInfoResponse:
    u = await user.get_current(context)
    if u is None:
        raise error.IdolError(error.ERROR_CODE_LIB_ERROR, 500, "User is not known", http_code=500)
    return UserInfoResponse(
        user=await user.get_user_info(context, u),
        ad_status=False,
        server_timestamp=util.time(),
    )


@idol.register("user", "setNotificationToken", batchable=False)
async def user_setnotificationtoken(context: idol.SchoolIdolUserParams, request: UserNotificationTokenRequest):
    # TODO
    util.stub("user", "setNotificationToken", request)
    return idol.core.DummyModel()


@idol.register("user", "changeNavi")
async def user_changenavi(context: idol.SchoolIdolUserParams, request: UserChangeNaviRequest) -> None:
    current_user = await user.get_current(context)
    unit_data = await unit.get_unit(context, request.unit_owning_user_id)
    unit.validate_unit(current_user, unit_data)
    await unit.set_unit_center(context, current_user, unit_data)
