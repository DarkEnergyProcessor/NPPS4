from .. import idol
from .. import util


@idol.register("/ad/changeAd")
async def ad_adchange(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /ad/changeAd", severity=util.logging.WARNING)
    return idol.core.DummyModel()
