import enum

import pydantic


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


class ReleaseInfoData(pydantic.BaseModel):
    id: int
    key: str


class ResponseData[_S: pydantic.BaseModel](pydantic.BaseModel):
    response_data: _S
    release_info: list[ReleaseInfoData] = pydantic.Field(default_factory=list)
    status_code: int = 200


class ErrorResponse(pydantic.BaseModel):
    error_code: int
    detail: str | None
