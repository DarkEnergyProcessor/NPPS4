import enum

import pydantic

from typing import TypeVar, Generic


class Language(str, enum.Enum):
    en = "en"
    jp = "jp"


class PlatformType(enum.IntEnum):
    iOS = 1
    Android = 2


class XMCVerifyMode(enum.IntEnum):
    NONE = 0
    SHARED = 1
    CROSS = 2


_S = TypeVar("_S", bound=pydantic.BaseModel | list[pydantic.BaseModel])


class ReleaseInfoData(pydantic.BaseModel):
    id: int
    key: str


class ResponseData(pydantic.BaseModel, Generic[_S]):
    response_data: _S
    release_info: list[ReleaseInfoData] = pydantic.Field(default_factory=list)
    status_code: int = 200


class ErrorResponse(pydantic.BaseModel):
    error_code: int
    detail: str | None
