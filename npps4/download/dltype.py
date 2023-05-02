import pydantic


class Checksum(pydantic.BaseModel):
    md5: str = "d41d8cd98f00b204e9800998ecf8427e"
    sha256: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class BaseInfo(pydantic.BaseModel):
    url: str
    size: int
    checksums: Checksum


class UpdateInfo(BaseInfo):
    version: str


class BatchInfo(BaseInfo):
    packageId: int
