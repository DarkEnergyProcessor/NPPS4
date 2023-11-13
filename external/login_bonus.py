# NPPS4 example Login Bonus Calendar file.
# This defines rewards given to players during the daily login bonus.
# You can specify other, vanilla Python file, but it must match
# the function specification below.
import datetime

START_OF_EPOCH = datetime.date(1970, 1, 1)


# Login bonus calendar file must define "get_rewards" async function with these parameters:
# * "day" (int)
# * "month" (int)
# * "year" (int)
# * "context" (npps4.idol.BasicSchoolIdolParams) to access the database.
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
