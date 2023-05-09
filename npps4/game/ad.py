from .. import idol
from .. import util

import pydantic


@idol.register("/ad/changeAd")
def ad_adchange(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /ad/changeAd", severity=util.logging.WARNING)
    return pydantic.BaseModel()
