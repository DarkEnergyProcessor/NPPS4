import pydantic

from typing import Generic, TypeVar

_T = TypeVar("_T")


class BeforeAfter(pydantic.BaseModel, Generic[_T]):
    before: _T
    after: _T
