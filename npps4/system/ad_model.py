import pydantic

from . import common


class AdInfo(pydantic.BaseModel):
    ad_id: int = 0
    term_id: int = 0
    reward_list: list[pydantic.SerializeAsAny[common.AnyItem]] = pydantic.Field(default_factory=list)
