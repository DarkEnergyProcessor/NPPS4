import pydantic

from .. import idol
from .. import util
from ..idol.system import live
from ..idol.system import user


class CommonLiveResumeRequest(pydantic.BaseModel):
    cancel: bool


@idol.register("common", "liveResume")
async def common_liveresume(context: idol.SchoolIdolUserParams, request: CommonLiveResumeRequest) -> None:
    if request.cancel:
        current_user = await user.get_current(context)
        await live.clean_live_in_progress(context, current_user)
