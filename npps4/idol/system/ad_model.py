import pydantic

from . import item_model


class AdInfo(pydantic.BaseModel):
    ad_id: int = 0
    term_id: int = 0
    reward_list: list[item_model.Item] = pydantic.Field(default_factory=list)
