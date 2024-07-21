import pydantic

from .. import idol
from .. import util


class MarathonInfoEventScenarioStatus(pydantic.BaseModel):
    title: str
    chapter: int
    is_reward: bool
    open_date: str
    title_font: str | None = None
    asset_bgm_id: int
    status_origin: int
    title_call_asset: str | None = None
    event_scenario_id: int
    open_total_event_point: int


class MarathonInfoEventScenario(pydantic.BaseModel):
    progress: int
    event_scenario_status: list[MarathonInfoEventScenarioStatus]


class MarathonInfoData(pydantic.BaseModel):
    event_id: int
    point_name: str
    event_point: int
    event_scenario: MarathonInfoEventScenario
    point_icon_asset: str
    total_event_point: int


class MarathonInfoResponse(pydantic.RootModel):
    root: list[MarathonInfoData]


@idol.register("marathon", "marathonInfo")
async def marathon_marathoninfo(context: idol.SchoolIdolUserParams) -> MarathonInfoResponse:
    # TODO
    util.stub("marathon", "marathonInfo", context.raw_request_data)
    return MarathonInfoResponse([])
