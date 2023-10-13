from .. import idol
from .. import util

import pydantic


class EventScenarioStatusResponse(pydantic.BaseModel):
    event_scenario_list: list


@idol.register("/eventscenario/status")
async def eventscenario_status(context: idol.SchoolIdolUserParams) -> EventScenarioStatusResponse:
    # TODO
    util.log("STUB /eventscenario/status", severity=util.logging.WARNING)
    return EventScenarioStatusResponse(event_scenario_list=[])
