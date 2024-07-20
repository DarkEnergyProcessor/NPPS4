from .. import idol
from ..system import common
from ..system import reward
from ..system import user


class AnnounceStateResponse(common.TimestampMixin):
    present_cnt: int
    has_unread_announce: bool


@idol.register("announce", "checkState")
async def announce_checkstate(context: idol.SchoolIdolUserParams) -> AnnounceStateResponse:
    current_user = await user.get_current(context)
    return AnnounceStateResponse(
        present_cnt=await reward.count_presentbox(context, current_user),
        has_unread_announce=False,  # TODO
    )
