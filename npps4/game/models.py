import pydantic

class UserData(pydantic.BaseModel):
    user_id: int
    name: str
    level: int

class CenterUnitInfo(pydantic.BaseModel):
    unit_id: int
    level: int
    love: int
    rank: int
    display_rank: int
    smile: int
    cute: int
    cool: int
    is_love_max: bool
    is_rank_max: bool
    is_level_max: bool
    unit_skill_exp: int
    removable_skill_ids: list[int]
    unit_removable_skill_capacity: int
