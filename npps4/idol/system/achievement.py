import dataclasses

import pydantic


class Achievement(pydantic.BaseModel):
    achievement_id: int
    count: int
    is_accomplished: bool
    insert_date: str
    end_date: str | None = None
    remaining_time: str = ""
    is_new: bool
    for_display: bool
    is_locked: bool
    open_condition_string: str = ""
    accomplish_id: str = ""


@dataclasses.dataclass
class AchievementContext:
    accomplished: list[Achievement] = dataclasses.field(default_factory=list)
    new: list[Achievement] = dataclasses.field(default_factory=list)
