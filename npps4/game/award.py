from .. import idol
from .. import util

import pydantic


class AwardInfo(pydantic.BaseModel):
    award_id: int
    is_set: bool
    insert_date: str


class AwardInfoResponse(pydantic.BaseModel):
    award_info: list[AwardInfo]


@idol.register("/award/awardInfo")
def award_awardinfo(context: idol.SchoolIdolUserParams) -> AwardInfoResponse:
    # TODO
    util.log("STUB /award/awardInfo", severity=util.logging.WARNING)
    return AwardInfoResponse(
        award_info=[
            AwardInfo(award_id=1, is_set=True, insert_date=util.timestamp_to_datetime(1365984000)),
            AwardInfo(award_id=23, is_set=False, insert_date=util.timestamp_to_datetime()),
        ]
    )
