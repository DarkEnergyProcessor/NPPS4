import pydantic

from .. import idol
from .. import util
from ..idol import session
from ..system import common
from ..system import handover
from ..system import user


class HandoverExecRequest(pydantic.BaseModel):
    handover_code: str
    handover_id: str


class KIDInfoResponse(common.TimestampMixin):
    auth_url: str


class KIDStatusResponse(common.TimestampMixin):
    has_klab_id: bool


class HandoverReserveTransferResponse(pydantic.BaseModel):
    invite_code: str
    code: str
    insert_date: str = pydantic.Field(default_factory=util.timestamp_to_datetime)


class KIDCheckRequest(pydantic.BaseModel):
    auth_code: str


class KIDCheckUserInfo(pydantic.BaseModel):
    user_id: str
    name: str
    level: int


class KIDCheckResponse(common.TimestampMixin):
    user_info: KIDCheckUserInfo


# TODO: Add into config.toml?
REROLL_TRANSFER_ID = "nil"
REROLL_TRANSFER_PASSCODE = "nil"
_REROLL_PASSCODE = handover.generate_passcode_sha1(REROLL_TRANSFER_ID, REROLL_TRANSFER_PASSCODE)


@idol.register("handover", "exec", batchable=False)
async def handover_exec(context: idol.SchoolIdolUserParams, request: HandoverExecRequest) -> None:
    # Special case for "nil", "nil":
    current_user = await user.get_current(context)

    if request.handover_id == REROLL_TRANSFER_ID and request.handover_code == _REROLL_PASSCODE:
        if current_user.level == 1:
            # Really?
            raise idol.error.by_code(idol.error.ERROR_HANDOVER_EXPIRE)

        # Reroll
        assert current_user.key is not None and current_user.passwd is not None
        target_user = await user.create(context, current_user.key, current_user.passwd)
    else:
        target_user = await handover.find_user_by_passcode(context, request.handover_code)
        if target_user is None:
            raise idol.error.by_code(idol.error.ERROR_HANDOVER_INVALID_ID_OR_CODE)
        # Sanity checks
        if target_user.locked:
            raise idol.error.by_code(idol.error.ERROR_HANDOVER_LOCKED_USER)
        if target_user.id == current_user.id:
            raise idol.error.by_code(idol.error.ERROR_HANDOVER_SELF)

    handover.swap_credentials(current_user, target_user)
    target_user.transfer_sha1 = None
    await session.invalidate_current(context)


@idol.register("handover", "kidInfo")
async def handover_kidinfo(context: idol.SchoolIdolUserParams) -> KIDInfoResponse:
    # TODO
    util.stub("handover", "kidInfo", context.raw_request_data)
    raise idol.error.by_code(idol.error.ERROR_KLAB_ID_SERVICE_MAINTENANCE)
    # return KIDInfoResponse(auth_url=str(context.request.url))


@idol.register("handover", "kidStatus")
async def handover_kidstatus(context: idol.SchoolIdolUserParams) -> KIDStatusResponse:
    # TODO
    util.stub("handover", "kidStatus", context.raw_request_data)
    return KIDStatusResponse(has_klab_id=False)


@idol.register("handover", "reserveTransfer", batchable=False)
async def handover_reservetransfer(context: idol.SchoolIdolUserParams) -> HandoverReserveTransferResponse:
    current_user = await user.get_current(context)
    transfer_code = handover.generate_transfer_code()
    current_user.transfer_sha1 = handover.generate_passcode_sha1(current_user.invite_code, transfer_code)

    return HandoverReserveTransferResponse(invite_code=current_user.invite_code, code=transfer_code)


@idol.register("handover", "abortTransfer", batchable=False)
async def handover_aborttransfer(context: idol.SchoolIdolUserParams) -> None:
    current_user = await user.get_current(context)
    current_user.transfer_sha1 = None


@idol.register("handover", "kidCheck", batchable=False)
async def handover_kidcheck(context: idol.SchoolIdolUserParams, request: KIDCheckRequest) -> KIDCheckResponse:
    # TODO
    util.stub("handover", "kidCheck", request)
    raise idol.error.by_code(idol.error.ERROR_KLAB_ID_SERVICE_NOT_REGISTERED)


@idol.register("handover", "kidHandover", batchable=False)
async def handover_kidhandover(context: idol.SchoolIdolUserParams) -> None:
    # TODO
    util.stub("handover", "kidHandover")
    raise idol.error.by_code(idol.error.ERROR_KLAB_ID_SERVICE_NOT_REGISTERED)


@idol.register("handover", "kidRegister", batchable=False)
async def handover_kidregister(context: idol.SchoolIdolUserParams, request: KIDCheckRequest) -> None:
    # TODO
    util.stub("handover", "kidRegister", request)
    raise idol.error.by_code(idol.error.ERROR_KLAB_ID_SERVICE_ALREADY_REGISTERED)
