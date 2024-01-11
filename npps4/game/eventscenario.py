from .. import idol
from .. import util

import pydantic


class EventScenarioStatusResponse(pydantic.BaseModel):
    event_scenario_list: list


@idol.register("eventscenario", "status")
async def eventscenario_status(context: idol.SchoolIdolUserParams) -> EventScenarioStatusResponse:
    # TODO
    util.stub("eventscenario", "status", context.raw_request_data)
    return EventScenarioStatusResponse(event_scenario_list=[])
