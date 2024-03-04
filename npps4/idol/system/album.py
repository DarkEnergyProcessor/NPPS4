import sqlalchemy

from . import achievement
from ... import idol
from ...db import main
from ...db import unit


async def update(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    /,
    unit_id: int,
    rank_max: bool = False,
    love_max: bool = False,
    rank_level_max: bool = False,
    highest_love: int = 0,
    favorite_point: int = 0,
    sign_flag: bool = False,
):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id, main.Album.unit_id == unit_id)
    result = await context.db.main.execute(q)
    album = result.scalar()

    if album is None:
        album = main.Album(
            user_id=user.id,
            unit_id=unit_id,
            rank_max_flag=False,
            love_max_flag=False,
            rank_level_max_flag=False,
            highest_love_per_unit=0,
            favorite_point=0,
            sign_flag=False,
        )
        context.db.main.add(album)

    album.rank_max_flag = rank_max or album.rank_max_flag
    album.love_max_flag = love_max or album.love_max_flag
    album.rank_level_max_flag = rank_level_max or album.rank_level_max_flag
    album.highest_love_per_unit = max(album.highest_love_per_unit, highest_love)
    album.favorite_point = max(album.favorite_point, favorite_point)
    album.sign_flag = sign_flag or album.sign_flag
    await context.db.main.flush()


async def all(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def all_series(context: idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(unit.AlbumSeries)
    result = await context.db.unit.execute(q)
    return {i.album_series_id: list() for i in result.scalars()}


async def count_album_with(context: idol.BasicSchoolIdolContext, user: main.User, *criteria):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Album)
        .where(main.Album.user_id == user.id, *criteria)
    )
    qc = await context.db.main.execute(q)
    return qc.scalar() or 0


async def trigger_achievement(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    *,
    obtained: bool = False,
    idolized: bool = False,
    max_love: bool = False,
    max_level: bool = False,
):
    """
    Check for achievement type 18 through 21
    """

    ach_ctx = achievement.AchievementContext()

    if obtained:
        count = await count_album_with(context, user)
        result = await achievement.check_type_18(context, user, count)
        ach_ctx.extend(result)

    if idolized:
        count = await count_album_with(context, user, main.Album.rank_max_flag == True)
        result = await achievement.check_type_19(context, user, count)
        ach_ctx.extend(result)

    if max_love:
        count = await count_album_with(context, user, main.Album.love_max_flag == True)
        result = await achievement.check_type_20(context, user, count)
        ach_ctx.extend(result)

    if max_level:
        count = await count_album_with(context, user, main.Album.rank_level_max_flag == True)
        result = await achievement.check_type_21(context, user, count)
        ach_ctx.extend(result)

    return ach_ctx
