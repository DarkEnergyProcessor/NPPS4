# NPPS4 example Login Bonus Calendar file.
# This defines rewards given to players during the daily login bonus.
# You can specify other, vanilla Python file, but it must match
# the function specification below.
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

import datetime

START_OF_EPOCH = datetime.date(1970, 1, 1)


# Login bonus calendar file must define "get_rewards" async function with these parameters:
# * "day" (int)
# * "month" (int)
# * "year" (int)
# * "context" (npps4.idol.BasicSchoolIdolContext) to access the database.
#
# It then returns 4 values in a tuple in exactly this order:
# * "add_type" (int), consult game_mater.db_ for details.
# * "item_id" (int), consult game_mater.db_ and item.db_ for details (depends on add_type).
# * "amount" (int)
# * "special_day" (tuple[str, str|None]|None), If it's special day, specify special day image asset for Japanese
#   language and optionally for English language (which can be None).
async def get_rewards(day: int, month: int, year: int, context) -> tuple[int, int, int, tuple[str, str | None] | None]:
    delta = datetime.date(year, month, day) - START_OF_EPOCH
    match delta.days % 3:
        case 0:
            # 20000 G
            return (3000, 3, 20000, None)
        case 1:
            # 2500 Friend Points
            return (3002, 2, 2500, None)
        case _:
            # 1 Loveca
            return (3001, 4, 1, None)
