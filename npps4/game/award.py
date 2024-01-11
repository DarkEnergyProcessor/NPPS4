import pydantic

from .. import idol
from .. import util
from ..idol import error
from ..idol.system import award
from ..idol.system import user


class AwardInfo(pydantic.BaseModel):
    award_id: int
    is_set: bool
    insert_date: str


class AwardInfoResponse(pydantic.BaseModel):
    award_info: list[AwardInfo]


class AwardSetRequest(pydantic.BaseModel):
    award_id: int


@idol.register("award", "awardInfo")
async def award_awardinfo(context: idol.SchoolIdolUserParams) -> AwardInfoResponse:
    current_user = await user.get_current(context)
    awards = await award.get_awards(context, current_user)
    award_info = [
        AwardInfo(
            award_id=aw.award_id,
            is_set=current_user.active_award == aw.award_id,
            insert_date=util.timestamp_to_datetime(aw.insert_date),
        )
        for aw in awards
    ]

    return AwardInfoResponse(award_info=award_info)


@idol.register("award", "set")
async def award_set(context: idol.SchoolIdolUserParams, request: AwardSetRequest) -> idol.core.DummyModel:
    current_user = await user.get_current(context)
    if await award.has_award(context, current_user, request.award_id):
        current_user.active_award = request.award_id
        return idol.core.DummyModel()

    raise error.IdolError(detail="No such award")
