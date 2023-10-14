from .. import idol
from .. import util


@idol.register("/marathon/marathonInfo")
async def marathon_marathoninfo(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /marathon/marathonInfo", severity=util.logging.WARNING)
    return idol.core.DummyModel()
