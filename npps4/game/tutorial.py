from .. import idol
from ..idol import error
from ..system import tutorial
from ..system import user

import pydantic


class TutorialProgressRequest(pydantic.BaseModel):
    tutorial_state: int


@idol.register("tutorial", "progress", batchable=False)
async def tutorial_progress(context: idol.SchoolIdolUserParams, request: TutorialProgressRequest) -> None:
    current_user = await user.get_current(context)
    if current_user.tutorial_state == -1:
        raise error.IdolError(detail="Tutorial already finished")

    if current_user.tutorial_state == 0 and request.tutorial_state == 1:
        await tutorial.phase1(context, current_user)
    elif current_user.tutorial_state == 1 and request.tutorial_state == 2:
        await tutorial.phase2(context, current_user)
    elif current_user.tutorial_state == 2 and request.tutorial_state == 3:
        await tutorial.phase3(context, current_user)
    elif current_user.tutorial_state == 3 and request.tutorial_state == -1:
        await tutorial.finalize(context, current_user)
    else:
        raise error.IdolError(detail=f"Unknown state, u {current_user.tutorial_state} r {request.tutorial_state}")


@idol.register("tutorial", "skip", batchable=False)
async def tutorial_skip(context: idol.SchoolIdolUserParams) -> None:
    current_user = await user.get_current(context)
    if current_user.tutorial_state == -1:
        raise error.IdolError(detail="Tutorial already finished")

    match current_user.tutorial_state:
        case 0:
            await tutorial.phase1(context, current_user)
            await tutorial.phase2(context, current_user)
            await tutorial.phase3(context, current_user)
            await tutorial.finalize(context, current_user)
        case 1:
            await tutorial.phase2(context, current_user)
            await tutorial.phase3(context, current_user)
            await tutorial.finalize(context, current_user)
        case 2:
            await tutorial.phase3(context, current_user)
            await tutorial.finalize(context, current_user)
        case 3:
            await tutorial.finalize(context, current_user)
        case _:
            raise error.IdolError(detail=f"Invalid tutorial state: {current_user.tutorial_state}")
