import sqlalchemy

from ... import idol
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
    # TODO: Achievements
    return []


async def all(context: idol.BasicSchoolIdolContext, user: main.User):
    q = sqlalchemy.select(main.Album).where(main.Album.user_id == user.id)
    result = await context.db.main.execute(q)
    return list(result.scalars())
