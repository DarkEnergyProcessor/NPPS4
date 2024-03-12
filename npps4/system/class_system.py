import pydantic

from .. import util


class ClassRankInfoData(pydantic.BaseModel):  # TODO
    before_class_rank_id: int = 1
    after_class_rank_id: int = 1
    rank_up_date: str = util.timestamp_to_datetime(86400)


class ClassSystemData(pydantic.BaseModel):  # TODO
    rank_info: ClassRankInfoData = pydantic.Field(default_factory=ClassRankInfoData)
    complete_flag: bool = False
    is_opened: bool = False
    is_visible: bool = False
