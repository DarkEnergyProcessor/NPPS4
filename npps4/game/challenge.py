from .. import idol
from .. import util


@idol.register("/challenge/challengeInfo")
async def challenge_challengeinfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /challenge/challengeInfo", severity=util.logging.WARNING)
    return idol.core.DummyModel()
