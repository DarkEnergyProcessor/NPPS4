from .. import idol
from .. import util

import pydantic


@idol.register("/challenge/challengeInfo")
def challenge_challengeinfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /challenge/challengeInfo", severity=util.logging.WARNING)
    return pydantic.BaseModel()
