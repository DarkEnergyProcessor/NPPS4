from .. import idol
from ..idol.system import subscenario
from ..idol.system import user

import pydantic


class SubScenarioStatus(pydantic.BaseModel):
    subscenario_id: int
    status: int


class SubScenarioStatusResponse(pydantic.BaseModel):
    subscenario_status_list: list[SubScenarioStatus]
    unlocked_subscenario_ids: list[int]


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
