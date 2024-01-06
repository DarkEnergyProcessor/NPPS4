# NPPS4 sample beatmap provider file.
# This sensible default load beatmaps from `beatmaps` folder.
# Please read the comments on how to implement your own beatmap provider.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the public
# domain. We make this dedication for the benefit of the public at large and to
# the detriment of our heirs and successors. We intend this dedication to be an
# overt act of relinquishment in perpetuity of all present and future rights to
# this software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import json
import os

import pydantic

import npps4.config.config

from typing import Iterable, Literal


# Implementation must return an object that has these attributes in their classes.
class BeatmapData(pydantic.BaseModel):
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
        with open(os.path.join(npps4.config.config.ROOT_DIR, "beatmaps", livejson), "r", encoding="UTF-8") as f:
            jsondata = f.read()
    except IOError:
        return None

    try:
        jsondata = json.loads(jsondata)
    except json.JSONDecodeError:
        return None

    result: list[BeatmapData] = []
    try:
        for jdata in jsondata:
            beatmap = BeatmapData.model_validate(jdata)
            result.append(beatmap)
    except pydantic.ValidationError:
        return None

    return result


# Beatmap provider file must define "randomize_beatmaps" async function with these parameters:
# * "beatmap" (iterable of BeatmapData)
# * "seed" (bytes) with length of 16. It's up to implementation how to use this seed.
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
# Note: The underlying beatmap data type of the iterable is same as the ones in "get_beatmap_data".
async def randomize_beatmaps(beatmap: Iterable[BeatmapData], seed: bytes, context) -> Iterable[BeatmapData]:
    # TODO: https://github.com/DarkEnergyProcessor/livesim2_async/blob/over_the_rainbow/game/live/randomizer3.lua
    return beatmap
