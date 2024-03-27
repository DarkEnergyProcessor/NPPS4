import pydantic

from . import item_model
from ..const import ADD_TYPE

from typing import Literal


class LiveNote(pydantic.BaseModel):
    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float = 1.0  # Higher = slower. Lower = faster.
    vanish: Literal[0, 1, 2] = 0  # 0 = Normal. 1 = Hidden. 2 = Sudden.


class LiveInfo(pydantic.BaseModel):
    live_difficulty_id: int
    is_random: bool = False
    ac_flag: int = 0
    swing_flag: int = 0


class LiveInfoWithNotes(LiveInfo):
    notes_list: list[LiveNote]


class LiveStatus(pydantic.BaseModel):
    live_difficulty_id: int
    status: int
    hi_score: int
    hi_combo_count: int
    clear_cnt: int
    achieved_goal_id_list: list[int]


class LiveItem(item_model.Item):
    add_type: int = ADD_TYPE.LIVE
    additional_normal_live_status_list: list[LiveStatus] = pydantic.Field(default_factory=list)
    additional_training_live_status_list: list[LiveStatus] = pydantic.Field(default_factory=list)  # TODO: Maybe
