import fastapi

from .. import idoltype
from ..download import dltype

from typing import Iterable, Literal, Protocol, Any


class LoginBonusProtocol(Protocol):
    async def get_rewards(
        self, day: int, month: int, year: int, context
    ) -> tuple[int, int, int, tuple[str, str | None] | None]: ...


class BadwordsCheckProtocol(Protocol):
    async def has_badwords(self, text: str, context) -> bool: ...


class BeatmapData(Protocol):
    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float  # Beatmap speed multipler
    vanish: Literal[0, 1, 2]  # 0 = Normal; 1 = Note hidden as it approaches; 2 = Note shows just before its timing.


class BeatmapProviderProtocol(Protocol):
    async def get_beatmap_data(self, livejson: str, context) -> Iterable[BeatmapData] | None: ...

    async def randomize_beatmaps(
        self, beatmap: Iterable[BeatmapData], seed: bytes, context
    ) -> Iterable[BeatmapData]: ...


class LiveUnitDropProtocol(Protocol):
    async def get_live_drop_unit(self, live_setting_id: int, context) -> int: ...


class DownloadBackendProtocol(Protocol):
    def initialize(self): ...

    def get_server_version(self) -> tuple[int, int]: ...

    def get_db_path(self, name: str) -> str: ...

    async def get_update_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, from_client_version: tuple[int, int]
    ) -> list[dltype.UpdateInfo]: ...

    async def get_batch_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, exclude: list[int]
    ) -> list[dltype.BatchInfo]: ...

    async def get_single_package(
        self, request: fastapi.Request, platform: idoltype.PlatformType, package_type: int, package_id: int
    ) -> list[dltype.BaseInfo] | None: ...

    async def get_raw_files(
        self, request: fastapi.Request, platform: idoltype.PlatformType, files: list[str]
    ) -> list[dltype.BaseInfo]: ...


class LiveDropBoxResult(Protocol):
    new_live_effort_point_box_spec_id: int
    offer_limited_effort_event_id: int
    rewards: list[tuple[int, int, int, dict[str, Any] | None]]


class LiveDropBoxProtocol(Protocol):
    async def process_effort_box(
        self, context, current_live_effort_point_box_spec_id: int, current_limited_effort_event_id: int, score: int
    ) -> LiveDropBoxResult: ...
