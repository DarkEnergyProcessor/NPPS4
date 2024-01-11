from .. import idol
from .. import util
from ..idol.system import scenario
from ..idol.system import user

import pydantic


class ScenarioStatus(pydantic.BaseModel):
    scenario_id: int
    status: int


class ScenarioStatusResponse(pydantic.BaseModel):
    scenario_status_list: list[ScenarioStatus]


class ScenarioStartupRequest(pydantic.BaseModel):
    scenario_id: int


class ScenarioStartupResponse(pydantic.BaseModel):
    scenario_id: int
    scenario_adjustment: int = 50  # TODO where to get this value


@idol.register("scenario", "scenarioStatus")
async def scenario_scenariostatus(context: idol.SchoolIdolUserParams) -> ScenarioStatusResponse:
    current_user = await user.get_current(context)
    scenarios = await scenario.get_all(context, current_user)
    return ScenarioStatusResponse(
        scenario_status_list=[ScenarioStatus(scenario_id=sc.scenario_id, status=1 + sc.completed) for sc in scenarios]
    )


@idol.register("scenario", "startup")
async def scenario_startup(
    context: idol.SchoolIdolUserParams, request: ScenarioStartupRequest
) -> ScenarioStartupResponse:
    # TODO
    util.stub("scenario", "startup", request)
    return ScenarioStartupResponse(scenario_id=request.scenario_id)
