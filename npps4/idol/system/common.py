import pydantic


class BeforeAfter(pydantic.BaseModel):
    before: int
    after: int
