from .. import idol
from .. import util


@idol.register("marathon", "marathonInfo")
async def marathon_marathoninfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.stub("marathon", "marathonInfo", context.raw_request_data)
    return idol.core.DummyModel()
