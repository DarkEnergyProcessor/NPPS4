# /subscenario/subscenarioStatus

from .. import idol
from .. import util

import pydantic


class SubScenarioStatusResponse(pydantic.BaseModel):
    subscenario_status_list: list
    unlocked_subscenario_ids: list[int]


@idol.register("/subscenario/subscenarioStatus")
def eventscenario_status(context: idol.SchoolIdolUserParams) -> SubScenarioStatusResponse:
    # TODO
    util.log("STUB /subscenario/subscenarioStatus", severity=util.logging.WARNING)
    return SubScenarioStatusResponse(subscenario_status_list=[], unlocked_subscenario_ids=[])
