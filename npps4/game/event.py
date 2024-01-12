import pydantic

from .. import idol
from .. import util


class EventTargetList(pydantic.BaseModel):
    position: int
    is_displayable: bool = True


class EventListResponse(pydantic.BaseModel):
    target_list: list[EventTargetList]
    server_timestamp: int = pydantic.Field(default_factory=util.time)


@idol.register("event", "eventList")
async def event_eventlist(context: idol.SchoolIdolUserParams) -> EventListResponse:
    util.stub("event", "eventList")
    raise idol.error.IdolError(idol.error.ERROR_CODE_EVENT_NO_EVENT_DATA, 600)
    # https://github.com/YumeMichi/honoka-chan/blob/6778972c1ff54a8a038ea07b676e6acdbb211f96/handler/event.go#L15
    # return EventListResponse(target_list=[EventTargetList(position=i, is_displayable=False) for i in range(1, 7)])
