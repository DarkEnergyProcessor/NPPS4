import pydantic

from . import item


class AdInfo(pydantic.BaseModel):
    ad_id: int = 0
    term_id: int = 0
    reward_list: list[item.Reward] = pydantic.Field(default_factory=list)
