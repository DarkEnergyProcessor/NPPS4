import pydantic
import sqlalchemy

from .. import idol
from ..db import main
from ..db import museum


class MuseumParameterData(pydantic.BaseModel):
    smile: int = 0
    pure: int = 0
    cool: int = 0


class MuseumInfoData(pydantic.BaseModel):
    parameter: MuseumParameterData
    contents_id_list: list[int]


async def unlock(context: idol.BasicSchoolIdolContext, user: main.User, museum_contents_id: int):
    if (await context.db.museum.get(museum.MuseumContents, museum_contents_id)) is None:
        raise ValueError("invalid museum contents id")

    q = sqlalchemy.select(main.MuseumUnlock).where(
        main.MuseumUnlock.user_id == user.id, main.MuseumUnlock.museum_contents_id == museum_contents_id
    )
    result = await context.db.main.execute(q)
    if result.scalar() is not None:
        return False

    museum_unlock = main.MuseumUnlock(user_id=user.id, museum_contents_id=museum_contents_id)
    context.db.main.add(museum_unlock)
    await context.db.main.flush()
    return True


async def has(context: idol.BasicSchoolIdolContext, user: main.User, museum_contents_id: int):
    q = sqlalchemy.select(main.MuseumUnlock).where(
        main.MuseumUnlock.user_id == user.id, main.MuseumUnlock.museum_contents_id == museum_contents_id
    )
    result = await context.db.main.execute(q)
    return result.scalar() is not None


TEST_MUSEUM_UNLOCK_ALL = False


async def get_museum_info_data(context: idol.BasicSchoolIdolContext, user: main.User):
    if TEST_MUSEUM_UNLOCK_ALL:
        q = sqlalchemy.select(museum.MuseumContents)
        result = await context.db.museum.execute(q)
        contents_id_list = [mu.museum_contents_id for mu in result.scalars()]
    else:
        q = sqlalchemy.select(main.MuseumUnlock).where(main.MuseumUnlock.user_id == user.id)
        result = await context.db.main.execute(q)
        contents_id_list = [mu.museum_contents_id for mu in result.scalars()]

    parameter = MuseumParameterData()
    q = sqlalchemy.select(museum.MuseumContents).where(museum.MuseumContents.museum_contents_id.in_(contents_id_list))
    result = await context.db.museum.execute(q)

    for mu in result.scalars():
        parameter.smile = parameter.smile + mu.smile_buff
        parameter.pure = parameter.pure + mu.pure_buff
        parameter.cool = parameter.cool + mu.cool_buff

    return MuseumInfoData(parameter=parameter, contents_id_list=contents_id_list)
