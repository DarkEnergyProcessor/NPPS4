import pydantic

from .. import const
from .. import idol
from .. import util
from ..system import common

from typing import Any


class NoticeMarquee(pydantic.BaseModel):
    # https://github.com/DarkEnergyProcessor/NPPS/blob/v3.1.x/modules/notice/noticeMarquee.php
    marquee_id: int
    text: str
    text_color: int
    display_place: int
    start_date: str
    end_date: str


class NoticeMarqueeResponse(pydantic.BaseModel):
    item_count: int
    marquee_list: list[NoticeMarquee]


class NoticeFriendVarietyRequest(pydantic.BaseModel):
    filter_id: int
    readed: bool
    page: int


class NoticeFriendVariety(pydantic.BaseModel):
    notice_id: int
    new_flag: bool
    reference_table: int
    filter_id: const.NOTICE_FILTER_ID
    notice_template_id: int
    message: str
    readed: bool
    insert_date: str
    affector: Any | None  # This is FriendSearchResponse


class NoticeFriendVarietyResponse(common.TimestampMixin):
    item_count: int
    notice_list: list[NoticeFriendVariety]


@idol.register("notice", "noticeMarquee")
async def notice_noticemarquee(context: idol.SchoolIdolUserParams) -> NoticeMarqueeResponse:
    # TODO
    util.stub("notice", "noticeMarquee", context.raw_request_data)
    return NoticeMarqueeResponse(item_count=0, marquee_list=[])


@idol.register("notice", "noticeFriendVariety")
async def notice_noticefriendvariety(
    context: idol.SchoolIdolUserParams, request: NoticeFriendVarietyRequest
) -> NoticeFriendVarietyResponse:
    # TODO
    util.stub("notice", "noticeFriendVariety", request)
    return NoticeFriendVarietyResponse(item_count=0, notice_list=[])
