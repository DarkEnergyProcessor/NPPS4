from .. import const
from .. import idol
from ..db import main


async def get_friend_status(context: idol.BasicSchoolIdolContext, /, current_user: main.User, target_user: main.User):
    # TODO
    if current_user.id == target_user.id:
        return const.FRIEND_STATUS.FRIEND
    return const.FRIEND_STATUS.OTHER
