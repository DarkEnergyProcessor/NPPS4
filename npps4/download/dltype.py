import pydantic


class Checksum(pydantic.BaseModel):
    md5: str
    sha256: str


class BaseInfo(pydantic.BaseModel):
    url: str
    size: int
    checksums: Checksum


class UpdateInfo(BaseInfo):
    version: str


class BatchInfo(BaseInfo):
    packageId: int
