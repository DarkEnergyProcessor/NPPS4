import pydantic

from .. import idol

from ..db import main
from ..idol.system import album
from ..idol.system import unit
from ..idol.system import user


class AlbumInfo(pydantic.BaseModel):
    unit_id: int
    rank_max_flag: bool
    love_max_flag: bool
    rank_level_max_flag: bool
    all_max_flag: bool
    highest_love_per_unit: int
    total_love: int
    favorite_point: int
    sign_flag: bool


class AlbumAllResponse(pydantic.RootModel[list[AlbumInfo]]):
    pass


class AlbumSeriesInfo(pydantic.BaseModel):
    series_id: int
    unit_list: list[AlbumInfo]


class AlbumSeriesAllResponse(pydantic.RootModel[list[AlbumSeriesInfo]]):
    pass


def album_to_response(data: main.Album):
    return AlbumInfo(
        unit_id=data.unit_id,
        rank_max_flag=data.rank_max_flag,
        love_max_flag=data.love_max_flag,
        rank_level_max_flag=data.rank_level_max_flag,
        all_max_flag=data.rank_max_flag and data.love_max_flag and data.rank_level_max_flag,
        highest_love_per_unit=data.highest_love_per_unit,
        total_love=data.highest_love_per_unit,  # TODO: Rectify this.
        favorite_point=data.favorite_point,
        sign_flag=data.sign_flag,
    )


def sort_by_series_id(data: AlbumSeriesInfo):
    return data.series_id


def sort_by_unit_id(data: AlbumInfo):
    return data.unit_id


@idol.register("album", "albumAll")
async def album_albumall(context: idol.SchoolIdolUserParams) -> AlbumAllResponse:
    current_user = await user.get_current(context)
    all_album = await album.all(context, current_user)
    return AlbumAllResponse.model_validate([album_to_response(a) for a in all_album])


@idol.register("album", "seriesAll")
async def album_seriesall(context: idol.SchoolIdolUserParams) -> AlbumSeriesAllResponse:
    current_user = await user.get_current(context)
    all_album = await album.all(context, current_user)
    series: dict[int, list[AlbumInfo]] = await album.all_series(context)

    for a in all_album:
        unit_info = await unit.get_unit_info(context, a.unit_id)
        if unit_info is not None and unit_info.album_series_id is not None:
            series[unit_info.album_series_id].append(album_to_response(a))

    return AlbumSeriesAllResponse.model_validate(
        sorted(
            [AlbumSeriesInfo(series_id=k, unit_list=sorted(v, key=sort_by_unit_id)) for k, v in series.items()],
            key=sort_by_series_id,
        )
    )
