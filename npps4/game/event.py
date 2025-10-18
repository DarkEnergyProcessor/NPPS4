import enum

import pydantic

from .. import idol
from .. import util
from ..system import common


class EventBonus(pydantic.BaseModel):
    limited_bonus_type: int
    limited_bonus_value: int


class EventCampaignList(pydantic.BaseModel):
    fixed_message: str = ""
    live_limited_bonuses: list[EventBonus]


class EventBannerType(enum.IntEnum):
    EVENT = 0
    DUEL = 7
    ARENA = 14
    CONCERT = 15
    CLASS_COMPETITION = 16
    CLASS = 17


class Event(pydantic.BaseModel):
    banner_type: EventBannerType
    asset_path: str
    start_date: str
    end_date: str
    is_locked: bool
    is_new: bool = True
    description: str = ""
    target_id: int | None = None
    # campaign_list: EventCampaignList | None = None


class EventTargetList(pydantic.BaseModel):
    position: int
    is_displayable: bool = True
    event_list: list[Event]


class EventListResponse(common.TimestampMixin):
    target_list: list[EventTargetList]


@idol.register("event", "eventList")
async def event_eventlist(context: idol.SchoolIdolUserParams) -> EventListResponse:
    util.stub("event", "eventList")
    raise idol.error.by_code(idol.error.ERROR_CODE_EVENT_NO_EVENT_DATA)
    # https://github.com/YumeMichi/honoka-chan/blob/6778972c1ff54a8a038ea07b676e6acdbb211f96/handler/event.go#L15
    # return EventListResponse(target_list=[EventTargetList(position=i, is_displayable=False) for i in range(1, 7)])
