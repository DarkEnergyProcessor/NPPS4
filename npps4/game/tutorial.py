from .. import idol
from .. import util

import pydantic


class TutorialProgressRequest(pydantic.BaseModel):
    tutorial_state: int


@idol.register("/tutorial/progress", batchable=False)
def tutorial_progress(context: idol.SchoolIdolUserParams, request: TutorialProgressRequest) -> pydantic.BaseModel:
    util.log("STUB /tutorial/progress", request, severity=util.logging.WARNING)
    return pydantic.BaseModel()
