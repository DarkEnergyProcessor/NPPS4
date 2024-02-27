import pydantic

from .. import idol
from .. import util


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


@idol.register("friend", "list")
async def friend_list(context: idol.SchoolIdolUserParams, request: FriendListRequest) -> FriendListResponse:
    # TODO
    util.stub("friend", "list", request)
    return FriendListResponse(item_count=0, friend_list=[], new_friend_list=[])


@idol.register("friend", "search")
async def friend_search(context: idol.SchoolIdolUserParams, request: FriendSearchRequest) -> idol.core.DummyModel:
    # TODO
    util.stub("friend", "search", request)
    raise idol.error.by_code(idol.error.ERROR_CODE_FRIEND_USER_NOT_EXISTS)
