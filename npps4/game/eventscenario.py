from .. import idol
from .. import util

import pydantic


class EventScenarioChapterList(pydantic.BaseModel):
    event_scenario_id: int
    amount: int
    status: int
    chapter: int
    item_id: int
    cost_type: int
    is_reward: bool
    open_flash_flag: int


class EventScenarioInfo(pydantic.BaseModel):
    event_id: int
    open_date: str
    chapter_list: list[EventScenarioChapterList]
    event_scenario_btn_asset: str  # "assets/image/ui/eventscenario/156_se_ba_t.png"
    event_scenario_se_btn_asset: str  # "assets/image/ui/eventscenario/156_se_ba_tse.png"


class EventScenarioStatusResponse(pydantic.BaseModel):
    event_scenario_list: list[EventScenarioInfo]


@idol.register("eventscenario", "status")
async def eventscenario_status(context: idol.SchoolIdolUserParams) -> EventScenarioStatusResponse:
    # TODO
    util.stub("eventscenario", "status", context.raw_request_data)
    return EventScenarioStatusResponse(event_scenario_list=[])
