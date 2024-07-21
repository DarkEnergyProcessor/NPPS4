import pydantic

from .. import idol
from .. import util


class ChallengeInfoDataBaseInfo(pydantic.BaseModel):
    event_id: int
    max_round: int
    event_point: int
    asset_bgm_id: int
    total_event_point: int


class ChallengeInfoDataStatus(pydantic.BaseModel):
    should_retire: bool
    should_proceed: bool
    should_finalize: bool


class ChallengeInfoData(pydantic.BaseModel):
    base_info: ChallengeInfoDataBaseInfo
    challenge_status: ChallengeInfoDataStatus


class ChallengeInfoResponse(pydantic.RootModel):
    root: ChallengeInfoData | idol.core.DummyModel


@idol.register("challenge", "challengeInfo")
async def challenge_challengeinfo(context: idol.SchoolIdolUserParams) -> ChallengeInfoResponse:
    # TODO
    util.stub("challenge", "challengeInfo", context.raw_request_data)
    return ChallengeInfoResponse(idol.core.DummyModel())
