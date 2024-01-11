from .. import idol
from .. import util


@idol.register("challenge", "challengeInfo")
async def challenge_challengeinfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.stub("challenge", "challengeInfo", context.raw_request_data)
    return idol.core.DummyModel()
