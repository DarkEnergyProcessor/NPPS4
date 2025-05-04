import dataclasses

import sqlalchemy

from .. import idol
from ..db import main
from ..db import unit


@dataclasses.dataclass
class Increment:
    value: int


async def update(
    context: idol.BasicSchoolIdolContext,
    user: main.User,
    /,
    unit_id: int,
    rank_max: bool = False,
    love_max: bool = False,
    rank_level_max: bool = False,
    highest_love: int | Increment = 0,
    favorite_point: int | Increment = 0,
    sign_flag: bool = False,
    *,
    flush: bool = True,
):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id, main.Album.unit_id == unit_id)
    result = await context.db.main.execute(q)
    album = result.scalar()

    if album is None:
        album = main.Album(user_id=user.id, unit_id=unit_id)
        context.db.main.add(album)

    album.rank_max_flag = rank_max or album.rank_max_flag
    album.love_max_flag = love_max or album.love_max_flag
    album.rank_level_max_flag = rank_level_max or album.rank_level_max_flag
    album.sign_flag = sign_flag or album.sign_flag

    if isinstance(highest_love, Increment):
        album.highest_love_per_unit = album.highest_love_per_unit + highest_love.value
    else:
        album.highest_love_per_unit = max(album.highest_love_per_unit, highest_love)
    if isinstance(favorite_point, Increment):
        album.favorite_point = album.favorite_point + favorite_point.value
    else:
        album.favorite_point = max(album.favorite_point, favorite_point)

    if flush:
        await context.db.main.flush()


async def all(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())


async def all_ranking(context: idol.BasicSchoolIdolContext, user: main.User):
    q = (
        sqlalchemy.select(main.Album)
        .where(main.Album.user_id == user.id)
        .order_by(main.Album.favorite_point.desc(), main.Album.id.desc())
        .limit(50)
    )
    result = await context.db.main.execute(q)
    return result.scalars().all()


async def all_series(context: idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(unit.AlbumSeries)
    result = await context.db.unit.execute(q)
    return {i.album_series_id: list() for i in result.scalars()}


async def count_album_with(
    context: idol.BasicSchoolIdolContext, user: main.User, *criteria: sqlalchemy.ColumnElement[bool]
):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.Album)
        .where(main.Album.user_id == user.id, *criteria)
    )
    qc = await context.db.main.execute(q)
    return qc.scalar() or 0


async def has_ever_got_unit(context: idol.BasicSchoolIdolContext, user: main.User, unit_id: int):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id, main.Album.unit_id == unit_id)
    result = await context.db.main.execute(q)
    return result.scalar() is not None
