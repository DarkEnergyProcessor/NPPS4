import pydantic

from .. import idol
from .. import util

from ..idol.system import album
from ..idol.system import user


class AlbumResponse(pydantic.BaseModel):
    unit_id: int
    rank_max_flag: bool
    love_max_flag: bool
    rank_level_max_flag: bool
    all_max_flag: bool
    highest_love_per_unit: int
    total_love: int
    favorite_point: int
    sign_flag: bool


@idol.register("/album/albumAll")
async def album_albumall(context: idol.SchoolIdolUserParams) -> list[AlbumResponse]:
    current_user = await user.get_current(context)
    all_album = await album.all(context, current_user)
    return [
        AlbumResponse(
            unit_id=a.unit_id,
            rank_max_flag=a.rank_max_flag,
            love_max_flag=a.love_max_flag,
            rank_level_max_flag=a.rank_level_max_flag,
            all_max_flag=a.rank_max_flag and a.love_max_flag and a.rank_level_max_flag,
            highest_love_per_unit=a.highest_love_per_unit,
            total_love=a.highest_love_per_unit,  # TODO: Rectify this.
            favorite_point=a.favorite_point,
            sign_flag=a.sign_flag,
        )
        for a in all_album
    ]
