from .. import idol
from .. import util

import pydantic


class MultiUnitScenarioResponse(pydantic.BaseModel):
    multi_unit_scenario_status_list: list


@idol.register("multiunit", "multiunitscenarioStatus")
async def multiunit_multiunitscenariostatus(context: idol.SchoolIdolUserParams) -> MultiUnitScenarioResponse:
    # TODO
    util.stub("multiunit", "multiunitscenarioStatus", context.raw_request_data)
    return MultiUnitScenarioResponse(multi_unit_scenario_status_list=[])
