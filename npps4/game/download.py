import enum
import time

from .. import idol
from .. import util
from ..idol import user
from ..idol import error

import pydantic


class DownloadTargetOS(str, enum.Enum):
    ANDROID = "Android"
    IPHONE = "iOS"


class DownloadPackageType(enum.IntEnum):
    BOOTSTRAP = 0
    LIVE = 1
    SCENARIO = 2
    SUBSCENARIO = 3
    MICRO = 4
    EVENT_SCENARIO = 5
    MULTI_UNIT_SCENARIO = 6


class DownloadUpdateRequest(pydantic.BaseModel):
    target_os: DownloadTargetOS
    install_version: str
    external_version: str
    package_list: list[int] = []


class DownloadBatchRequest(pydantic.BaseModel):
    client_version: str
    os: DownloadTargetOS
    package_type: DownloadPackageType
    excluded_package_ids: list[int] = []


class DownloadAdditionalRequest(pydantic.BaseModel):
    target_os: DownloadTargetOS
    client_version: str
    package_type: DownloadPackageType
    package_id: int


class DownloadResponse(pydantic.BaseModel):
    size: str
    url: str


class DownloadUpdateResponse(DownloadResponse):
    version: str


@idol.register("/download/update", check_version=False, batchable=False)
def update(context: idol.SchoolIdolAuthParams, request: DownloadUpdateRequest) -> list[DownloadUpdateResponse]:
    # TODO
    raise error.IdolError(error.ERROR_DOWNLOAD_NO_UPDATE_PACKAGE)
    return []


@idol.register("/download/batch", check_version=False, batchable=False)
@idol.register("/download/event", check_version=False, batchable=False)
def batch(context: idol.SchoolIdolAuthParams, request: DownloadBatchRequest) -> list[DownloadResponse]:
    # TODO
    raise error.IdolError(error.ERROR_DOWNLOAD_NO_ADDITIONAL_PACKAGE)
    return []


@idol.register("/download/additional", check_version=False, batchable=False)
def additional(context: idol.SchoolIdolAuthParams, request: DownloadAdditionalRequest) -> list[DownloadResponse]:
    # TODO
    raise error.IdolError(error.ERROR_DOWNLOAD_NO_ADDITIONAL_PACKAGE)
    return []
