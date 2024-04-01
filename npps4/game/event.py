import pydantic

from .. import idol
from .. import util
from ..system import common


class EventTargetList(pydantic.BaseModel):
    position: int
    is_displayable: bool = True


class EventListResponse(common.TimestampMixin):
    target_list: list[EventTargetList]


@idol.register("event", "eventList")
async def event_eventlist(context: idol.SchoolIdolUserParams) -> EventListResponse:
    util.stub("event", "eventList")
    raise idol.error.by_code(idol.error.ERROR_CODE_EVENT_NO_EVENT_DATA)
    # https://github.com/YumeMichi/honoka-chan/blob/6778972c1ff54a8a038ea07b676e6acdbb211f96/handler/event.go#L15
    # return EventListResponse(target_list=[EventTargetList(position=i, is_displayable=False) for i in range(1, 7)])
