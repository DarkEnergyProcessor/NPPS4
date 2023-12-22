from .. import idol
from .. import util
from ..idol.system import subscenario
from ..idol.system import user

import pydantic


class SubScenarioStatus(pydantic.BaseModel):
    subscenario_id: int
    status: int


class SubScenarioStatusResponse(pydantic.BaseModel):
    subscenario_status_list: list[SubScenarioStatus]
    unlocked_subscenario_ids: list[int]


class SubScenarioStartupRequest(pydantic.BaseModel):
    subscenario_id: int


class SubScenarioStartupResponse(pydantic.BaseModel):
    subscenario_id: int
    scenario_adjustment: int = 50  # TODO where to get this value


@idol.register("/subscenario/subscenarioStatus")
async def subscenario_status(context: idol.SchoolIdolUserParams) -> SubScenarioStatusResponse:
    current_user = await user.get_current(context)
    subscenarios = await subscenario.get_all(context, current_user)
    return SubScenarioStatusResponse(
        subscenario_status_list=[
            SubScenarioStatus(subscenario_id=sc.subscenario_id, status=1 + sc.completed) for sc in subscenarios
        ],
        unlocked_subscenario_ids=[],
    )


@idol.register("/subscenario/startup")
async def scenario_startup(
    context: idol.SchoolIdolUserParams, request: SubScenarioStartupRequest
) -> SubScenarioStartupResponse:
    # TODO
    util.stub("subscenario", "startup", request)
    return SubScenarioStartupResponse(subscenario_id=request.subscenario_id)
