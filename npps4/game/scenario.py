import itertools

from .. import idol
from .. import util

import pydantic


class ScenarioStatus(pydantic.BaseModel):
    scenario_id: int
    status: int


class ScenarioStatusResponse(pydantic.BaseModel):
    scenario_status_list: list[ScenarioStatus]


@idol.register("/scenario/scenarioStatus")
async def scenario_scenariostatus(context: idol.SchoolIdolUserParams) -> ScenarioStatusResponse:
    # TODO
    util.log("STUB /scenario/scenarioStatus", severity=util.logging.WARNING)
    return ScenarioStatusResponse(
        scenario_status_list=[
            ScenarioStatus(scenario_id=i, status=2) for i in itertools.chain(range(1, 4), range(184, 189))
        ]
    )
