# NPPS4 example Live Show! Reward Box ("live effort") drop.
# This file defines the behavior of Live Show! Reward Box, what effort box to give
# and whetever it should switch to limited reward box.
#
# Until more data is retrieved, the sensible configuration are as follows:
# * Reward box selection is based on 1/4 of the effort point score.
#   This means, completing a box with score of 1.1m will give 4m boxes and 900k score
#   will give 2m boxes.
# * The drop is configurable in `server_data.json`
# * The determination of limited reward box is currently non-functional and will act as
#   if no limited reward box is present. This is due to lack of drop data.
#
# Please read the comments on how to implement your own Live Show! Reward Box drop.
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

import dataclasses
import random

import sqlalchemy

import npps4.data
import npps4.db.effort
import npps4.idol

from typing import Any


@dataclasses.dataclass
class ProcessResult:
    new_live_effort_point_box_spec_id: int
    offer_limited_effort_event_id: int
    rewards: list[tuple[int, int, int, dict[str, Any] | None]]


# Custom Live Show! Reward Box drop file must define "process_effort_box" async function with these parameters:
# * "context" (npps4.idol.BasicSchoolIdolContext) to access the database.
# * "current_live_effort_point_box_spec_id" (int) current reward box.
# * "current_limited_effort_event_id" (int) current limited reward box or 0 if not in limited box.
# * "score" (int) Live Show! score (or increment amount), used to determine the next box.
#
# It then returns an object with these fields:
# * "new_live_effort_point_box_spec_id" (int) - The next effort point box to give.
# * "offer_limited_effort_event_id" (int) - Limited reward box ID to give, or 0 to keep the normal box.
# * "rewards" (list[tuple[int, int, int, dict[str, Any] | None]]) - Effort box reward. The tuple is:
#   [0] - add_type
#   [1] - item_id
#   [2] - amount
#   [3] - extra data (for unit), or None
async def process_effort_box(
    context: npps4.idol.BasicSchoolIdolContext,
    current_live_effort_point_box_spec_id: int,
    current_limited_effort_event_id: int,
    score: int,
):
    q = sqlalchemy.select(npps4.db.effort.LiveEffortPointBoxSpec).order_by(
        npps4.db.effort.LiveEffortPointBoxSpec.capacity.desc()
    )
    result = await context.db.effort.execute(q)
    effort_spec_list = list(result.scalars())

    # Determine the current effort box
    current_box: npps4.db.effort.LiveEffortPointBoxSpec | None = None
    for effort_spec in effort_spec_list:
        if effort_spec.live_effort_point_box_spec_id == current_live_effort_point_box_spec_id:
            current_box = effort_spec
            break

    next_box_id: int = 1
    # Determine the next effort box
    for effort_spec in effort_spec_list:
        if (score * 4) >= effort_spec.capacity:
            next_box_id = effort_spec.live_effort_point_box_spec_id
            break

    rewards: list[tuple[int, int, int, dict[str, Any] | None]] = []
    if current_box is not None:
        rewards.extend(_get_reward_from_box(current_box.live_effort_point_box_spec_id, current_box.num_rewards))

    return ProcessResult(
        new_live_effort_point_box_spec_id=next_box_id, offer_limited_effort_event_id=0, rewards=rewards
    )


server_data = None
cached_live_drops: dict[int, list[tuple[int, int, int, dict[str, Any] | None]]] = {}
_SYSRAND = random.SystemRandom()


def _refresh_drop_cache():
    global server_data
    current_server_data = npps4.data.get()

    if current_server_data != server_data:
        for live_effort_point_box_spec_id, drops in current_server_data.live_effort_drops.items():
            result: list[tuple[int, int, int, dict[str, Any] | None]] = []

            for drop in drops:
                extra_data: dict[str, Any] | None = None
                if hasattr(drop, "extra"):
                    extra_data = getattr(drop, "extra")

                result.extend([(drop.add_type, drop.item_id, drop.amount, extra_data)] * drop.weight)

            cached_live_drops[live_effort_point_box_spec_id] = result

        server_data = current_server_data


def _get_reward_from_box(live_effort_point_box_spec_id: int, amount: int, /):
    global cached_live_drops
    _refresh_drop_cache()

    result: list[tuple[int, int, int, dict[str, Any] | None]] = []
    if live_effort_point_box_spec_id in cached_live_drops:
        drops = cached_live_drops[live_effort_point_box_spec_id]
        for i in range(amount):
            result.append(_SYSRAND.choice(drops))

    return result
