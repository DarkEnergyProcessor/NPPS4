from .. import idol
from .. import util


@idol.register("ad", "changeAd")
async def ad_adchange(context: idol.SchoolIdolUserParams):
    # TODO
    util.stub("ad", "changeAd", context.raw_request_data)
    return idol.core.DummyModel()
