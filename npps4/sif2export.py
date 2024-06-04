import fastapi
import pydantic

from . import idol
from . import idoltype
from .app import app
from .system import album
from .system import award
from .system import handover

from typing import Annotated


class EWExportUnit(pydantic.BaseModel):
    id: int
    idolized: bool
    signed: bool


class EWExportResponse(pydantic.BaseModel):
    rank: int
    units: list[EWExportUnit]
    titles: list[int]


@app.core.get("/ewexport")
async def export_to_ew(sha1: Annotated[str, fastapi.Query()]):
    async with idol.BasicSchoolIdolContext(idoltype.Language.en) as context:
        target_user = await handover.find_user_by_passcode(context, sha1)
        if target_user is None:
            raise fastapi.HTTPException(404, "not found")

        all_album = await album.all(context, target_user)
        all_awards = await award.get_awards(context, target_user)

        return EWExportResponse(
            rank=target_user.level,
            units=[EWExportUnit(id=u.unit_id, idolized=u.rank_max_flag, signed=u.sign_flag) for u in all_album],
            titles=[t.award_id for t in all_awards],
        )
