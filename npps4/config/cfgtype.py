import fastapi

from .. import idoltype
from ..download import dltype

from typing import Protocol


class DownloadBackendProtocol(Protocol):
    def initialize(self):
        ...

    def get_server_version(self) -> tuple[int, int]:
        ...

    def get_db_path(self, name: str) -> str:
        ...

    async def get_update_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
    ) -> list[dltype.UpdateInfo]:
        ...

    async def get_batch_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
    ) -> list[dltype.BatchInfo]:
        ...

    async def get_single_package(
        self, request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
    ) -> list[dltype.BaseInfo] | None:
        ...

    async def get_raw_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]
    ) -> list[dltype.BaseInfo]:
        ...
