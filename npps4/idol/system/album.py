import sqlalchemy

from . import core
from ... import idol
from ... import idoltype
from ...db import main


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
    album.highest_love_per_unit = max(album.highest_love_per_unit, highest_love)
    album.favorite_point = max(album.favorite_point, favorite_point)
    album.sign_flag = sign_flag or album.sign_flag
    if flush:
        await context.db.main.flush()
