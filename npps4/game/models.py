import pydantic


class UserData(pydantic.BaseModel):
    user_id: int
    name: str
    level: int
