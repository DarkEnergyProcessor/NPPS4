# NPPS4 example Live Show! unit reward drop.
# This file defines the drops of each club members when clearing a live show.
# This sensible default is (configurable in server_data.json):
# * 10% of dropping R cards if the live setting allows.
# * 90% of dropping N cards.
# Please read the comments on how to implement your own Live Show! unit reward drop.
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

import random

import npps4.data
import npps4.idol

_SYSRAND = random.SystemRandom()

_last_server_data = None
_cached_rare_drops: dict[int, list[int]] = {}
_cached_common_drops: list[int] = []


def _rebuild_cache():
    global _cached_rare_drops, _cached_common_drops, _last_server_data
    server_data = npps4.data.get()

    if server_data != _last_server_data:
        # Rebuild common drop cache
        _cached_common_drops = []

        for unit_drop in server_data.common_live_unit_drops:
            _cached_common_drops.extend([unit_drop.unit_id] * unit_drop.weight)

        # Rebuild live specific drop cache
        _cached_rare_drops = {}

        for lsid, live_unit_drops in server_data.live_specific_live_unit_drops.items():
            by_lsid: list[int] = []

            for unit_drop in live_unit_drops:
                by_lsid.extend([unit_drop.unit_id] * unit_drop.weight)

            _cached_rare_drops[lsid] = by_lsid

        _last_server_data = server_data

    return server_data


def _get_drop_r(context: npps4.idol.BasicSchoolIdolContext, live_setting_id: int):
    global _cached_rare_drops
    unit_drops = _cached_rare_drops.get(live_setting_id)

    if unit_drops:
        return _SYSRAND.choice(unit_drops)

    return 0


def _get_drop_n(context: npps4.idol.BasicSchoolIdolContext, live_setting_id: int):
    global _cached_common_drops
    return _SYSRAND.choice(_cached_common_drops)


# Live Show! unit reward drop file must define "get_live_drop_unit" async function with these parameters:
# * "live_setting_id" (int) of the played beatmap as in their `live_setting_m`.
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
#
# It then returns an integer `unit_id` to give to player.
async def get_live_drop_unit(live_setting_id: int, context: npps4.idol.BasicSchoolIdolContext):
    global _last_server_data
    server_data = _rebuild_cache()
    unit_id = 0

    choice_func = [_get_drop_n] * server_data.live_unit_drop_chance.common + [
        _get_drop_r
    ] * server_data.live_unit_drop_chance.live_specific

    while unit_id == 0:
        unit_id = _SYSRAND.choice(choice_func)(context, live_setting_id)

    return unit_id
