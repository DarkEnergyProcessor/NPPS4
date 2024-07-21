from .. import idol
from .. import util

import pydantic


class MultiUnitSccenarioChapterList(pydantic.BaseModel):
    multi_unit_scenario_id: int
    status: int
    chapter: int


class MultiUnitSccenarioInfo(pydantic.BaseModel):
    multi_unit_id: int
    status: int
    open_date: str
    chapter_list: list[MultiUnitSccenarioChapterList]
    multi_unit_scenario_btn_asset: str  # "assets/image/scenario/banner/aqoth_21.png"
    multi_unit_scenario_se_btn_asset: str  # "assets/image/scenario/banner/aqoth_21se.png"


class MultiUnitScenarioResponse(pydantic.BaseModel):
    multi_unit_scenario_status_list: list[MultiUnitSccenarioInfo]


@idol.register("multiunit", "multiunitscenarioStatus")
async def multiunit_multiunitscenariostatus(context: idol.SchoolIdolUserParams) -> MultiUnitScenarioResponse:
    # TODO
    util.stub("multiunit", "multiunitscenarioStatus", context.raw_request_data)
    return MultiUnitScenarioResponse(multi_unit_scenario_status_list=[])
