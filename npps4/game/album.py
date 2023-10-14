from .. import idol
from .. import util


@idol.register("/album/albumAll")
async def album_albumall(context: idol.SchoolIdolUserParams):
    # TODO
    util.log("STUB /album/albumAll", severity=util.logging.WARNING)
    return idol.core.DummyModel()
