# ERROR_CODE_EVENT_NO_EVENT_DATA
from .. import idol
from .. import util


@idol.register("event", "eventList")
async def event_eventlist(context: idol.SchoolIdolUserParams) -> idol.core.DummyModel:
    util.stub("event", "eventList", context.raw_request_data)
    raise idol.error.IdolError(idol.error.ERROR_CODE_EVENT_NO_EVENT_DATA, 600)
