from .. import idol
from .. import util

import pydantic


class MultiUnitScenarioResponse(pydantic.BaseModel):
    multi_unit_scenario_status_list: list


@idol.register("/multiunit/multiunitscenarioStatus")
def multiunit_multiunitscenariostatus(context: idol.SchoolIdolUserParams) -> MultiUnitScenarioResponse:
    # TODO
    util.log("STUB /multiunit/multiunitscenarioStatus", severity=util.logging.WARNING)
    return MultiUnitScenarioResponse(multi_unit_scenario_status_list=[])
