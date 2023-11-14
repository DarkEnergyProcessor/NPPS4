# NPPS4 sample beatmap provider file.
# This sensible default load beatmaps from `beatmaps` folder.
# Please read the comments on how to implement your own beatmap provider.

import pydantic
import json
import os

import npps4.config

from typing import Iterable, Literal


# Implementation must return an object that has these attributes in their classes.
class BeatmapData(pydantic.BaseModel):
    """
    (parameter) definition: {
        effect: unknown,
        notes_attribute: unknown,
        notes_level: unknown,
        position: unknown,
        speed: unknown,
        timing_sec: unknown,
        vanish: unknown,
    }
    """

    timing_sec: float
    notes_attribute: int
    notes_level: int
    effect: int
    effect_value: float
    position: int
    speed: float = 1.0  # Beatmap speed multipler
    vanish: Literal[
        0, 1, 2
    ] = 0  # 0 = Normal; 1 = Note hidden as it approaches; 2 = Note shows just before its timing.


# Beatmap provider file must define "get_beatmap_data" async function with these parameters:
# * "livejson" (str) of the beatmap as in their live_setting_m
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
#
# It then returns an iterable of BeatmapData above or None if the beatmap is not found:
async def get_beatmap_data(livejson: str, context) -> Iterable[BeatmapData] | None:
    try:
        f = open(os.path.join(npps4.config.ROOT_DIR, "beatmaps", livejson), "r", encoding="UTF-8")
    except IOError:
        return None

    try:
        jsondata = json.load(f)
    except json.JSONDecodeError:
        return None

    result: list[BeatmapData] = []
    for jdata in jsondata:
        beatmap = BeatmapData.model_validate(jdata)
        result.append(beatmap)

    return result


# Beatmap provider file must define "randomize_beatmaps" async function with these parameters:
# * "beatmap" (iterable of BeatmapData)
# * "seed" (bytes) with length of 16. It's up to implementation how to use this seed.
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
# Note: The underlying beatmap data type of the iterable is same as the ones in "get_beatmap_data".
async def randomize_beatmaps(beatmap: Iterable[BeatmapData], seed: bytes, context) -> Iterable[BeatmapData]:
    # TODO: https://github.com/DarkEnergyProcessor/livesim2_async/blob/over_the_rainbow/game/live/randomizer3.lua
    return beatmap
