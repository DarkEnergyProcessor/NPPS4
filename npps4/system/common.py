import pydantic

from . import item_model
from . import live_model
from . import scenario_model
from . import unit_model
from .. import util


AnyItem = unit_model.AnyUnitItem | scenario_model.ScenarioItem | live_model.LiveItem | item_model.Item


class BeforeAfter[_T](pydantic.BaseModel):
    before: _T
    after: _T


class BaseRewardInfo(pydantic.BaseModel):
    game_coin: int
    game_coin_reward_box_flag: bool


class ItemCount(pydantic.BaseModel):
    item_id: int
    amount: int


class TimestampMixin(pydantic.BaseModel):
    server_timestamp: int = pydantic.Field(default_factory=util.time)
