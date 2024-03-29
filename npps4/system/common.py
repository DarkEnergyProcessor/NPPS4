import pydantic

from . import item_model
from ..system import live_model
from . import scenario_model
from . import unit_model

from typing import Generic, TypeVar

_T = TypeVar("_T")

AnyItem = (
    unit_model.UnitSupportItem
    | unit_model.UnitItem
    | scenario_model.ScenarioItem
    | live_model.LiveItem
    | item_model.Item
)


class BeforeAfter(pydantic.BaseModel, Generic[_T]):
    before: _T
    after: _T


class BaseRewardInfo(pydantic.BaseModel):
    game_coin: int
    game_coin_reward_box_flag: bool


class ItemCount(pydantic.BaseModel):
    item_id: int
    amount: int
