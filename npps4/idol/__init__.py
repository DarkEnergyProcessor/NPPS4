import enum
import dataclasses
import json
import time
import typing
import urllib.parse

import fastapi
import pydantic
import pydantic.generics
import sqlalchemy.orm

from . import error
from .. import app_main
from .. import config
from .. import db
from .. import util

from typing import Annotated, Callable, TypeVar, Generic, cast


class Language(str, enum.Enum):
    en = "en"
    jp = "jp"


class PlatformType(enum.IntEnum):
    iOS = 1
    Android = 2


class XMCVerifyMode(enum.IntEnum):
    NONE = 0
    SHARED = 1
    # self.xor(self.xor_base[16:], application_key[:16]) + self.xor(self.xor_base[:16], application_key[16:])
    CROSS = 2


class Database:
    def __init__(self) -> None:
        self._mainsession: sqlalchemy.orm.Session | None = None
        self._livesession: sqlalchemy.orm.Session | None = None
        self._unitsession: sqlalchemy.orm.Session | None = None

    @property
    def main(self):
        if self._mainsession is None:
            self._mainsession = db.main.get_session()
        return self._mainsession

    @property
    def live(self):
        if self._livesession is None:
            self._livesession = db.live.get_session()
        return self._livesession

    @property
    def unit(self):
        if self._unitsession is None:
            self._unitsession = db.unit.get_session()
        return self._unitsession

    def cleanup(self):
        if self._livesession is not None:
            self._livesession.close()
        if self._unitsession is not None:
            self._unitsession.close()


class SchoolIdolParams:
    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True)],
    ):
        authorize_parsed = dict(urllib.parse.parse_qsl(authorize))
        if authorize_parsed.get("consumerKey") != "lovelive_test":
            raise fastapi.HTTPException(422, detail="Invalid consumerKey")

        cv_parsed = client_version.split(".", 1)
        try:
            self.client_version = (int(cv_parsed[0]), int(cv_parsed[1]))
        except ValueError as e:
            raise fastapi.HTTPException(422, detail=str(e)) from None

        self.token_text = authorize_parsed.get("token")

        ts = int(time.time())
        try:
            self.timestamp = int(authorize_parsed.get("timeStamp", ts))
        except ValueError:
            self.timestamp = ts

        self.lang: Language = lang
        self.platform: PlatformType = platform_type
        self.x_message_code = request.headers.get("X-Message-Code")
        self.raw_request_data = request_data
        self.db = Database()


class SchoolIdolAuthParams(SchoolIdolParams):
    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True)],
    ):
        super().__init__(request, authorize, client_version, lang, platform_type, request_data)
        token = None
        if self.token_text is not None:
            token = util.decapsulate_token(self.token_text)

        if token is None:
            raise fastapi.HTTPException(403, detail="Invalid token")

        self.token = token


class SchoolIdolUserParams(SchoolIdolAuthParams):
    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True)],
    ):
        super().__init__(request, authorize, client_version, lang, platform_type, request_data)
        if self.token.user_id == 0:
            raise fastapi.HTTPException(403, detail="Not logged in!")


_S = TypeVar("_S", bound=pydantic.BaseModel)


class ResponseData(pydantic.generics.GenericModel, Generic[_S]):
    response_data: _S
    release_info: list[config.ReleaseInfoData] = []
    status_code: int = 200


class ErrorResponse(pydantic.BaseModel):
    error_code: int
    detail: str | None


_T = TypeVar("_T", bound=SchoolIdolParams)
_U = TypeVar("_U", bound=pydantic.BaseModel)
_V = TypeVar("_V", bound=pydantic.BaseModel)


@dataclasses.dataclass
class Endpoint(Generic[_T, _U, _V]):
    context_class: type[SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams]
    request_class: type[pydantic.BaseModel] | None
    function: Callable[
        [SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams, pydantic.BaseModel], pydantic.BaseModel
    ] | Callable[[SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams], pydantic.BaseModel]


def _get_request_data(model: type[pydantic.BaseModel]):
    def actual_getter(
        request_data: Annotated[pydantic.Json[model], fastapi.Form()],
        xmc: Annotated[str, fastapi.Header(alias="X-Message-Code")],
    ):
        return request_data

    return actual_getter


def client_check(context: SchoolIdolParams, check_version: bool, xmc_verify: XMCVerifyMode):
    # Maintenance check
    if config.is_maintenance():
        return fastapi.responses.JSONResponse(
            [],
            200,
            {
                "Maintenance": "1",
            },
        )

    # XMC check
    if config.need_xmc_verify() and context.raw_request_data is not None and xmc_verify != XMCVerifyMode.NONE:
        if context.x_message_code is None:
            raise fastapi.HTTPException(422, "Invalid X-Message-Code")
        if not isinstance(context, SchoolIdolAuthParams):
            raise fastapi.HTTPException(422, "Invalid X-Message-Code (no token)")

        if xmc_verify == XMCVerifyMode.SHARED:
            hmac_key = util.xorbytes(context.token.client_key, context.token.server_key)
        elif xmc_verify == XMCVerifyMode.CROSS:
            base = config.get_base_xorpad()
            appkey = config.get_application_key()
            hmac_key = util.xorbytes(base[16:], appkey[:16]) + util.xorbytes(base[:16], appkey[16:])
        else:
            raise fastapi.HTTPException(500, "Invalid X-Message-Code verification mode")

        xmc = util.hmac_sha1(context.raw_request_data, hmac_key)
        if xmc.hex().upper() != context.x_message_code.upper():
            raise fastapi.HTTPException(422, "X-Message-Code does not match")

    # Client-Version check
    if check_version:
        if config.get_latest_version() != context.client_version:
            return fastapi.responses.JSONResponse([], 200)
    return None


def build_response(context: SchoolIdolParams, response: pydantic.BaseModel, status_code: int = 200):
    response_data = {
        "response_data": response.dict(),
        "release_info": config.get_release_info_keys(),
        "status_code": status_code,
    }
    jsondata = json.dumps(response_data).encode("UTF-8")
    context.db.cleanup()
    return fastapi.responses.Response(
        jsondata,
        media_type="application/json",
        headers={
            "Server-Version": util.sif_version_string(config.get_latest_version()),
            "X-Message-Sign": util.sign_message(jsondata, context.x_message_code),
        },
    )


API_ROUTER_MAP: dict[str, Endpoint] = {}
RESPONSE_HEADERS = {"Server-Version": {"type": "string"}, "X-Message-Sign": {"type": "string"}}


def register(
    endpoint: str,
    *,
    check_version: bool = True,
    batchable: bool = True,
    xmc_verify: XMCVerifyMode = XMCVerifyMode.SHARED
):
    def wrap0(f: Callable[[_T, _U], _V] | Callable[[_T], _V]):
        nonlocal endpoint, check_version, batchable

        signature = typing.get_type_hints(f)
        params: list[type] = list(map(lambda x: x[1], filter(lambda x: x[0] != "return", signature.items())))
        ret: type[_V | pydantic.BaseModel] = signature.get("return", pydantic.BaseModel)

        if len(params) == 1:

            @app_main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            @app_main.get(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            def wrap1(context: Annotated[_T, fastapi.Depends(params[0])]):
                nonlocal ret, check_version, xmc_verify
                check = client_check(context, check_version, xmc_verify)
                if check is None:
                    try:
                        result: _V = f(context)  # type: ignore
                        return build_response(context, result)
                    except error.IdolError as e:
                        return build_response(
                            context, ErrorResponse(error_code=e.error_code, detail=e.detail), e.status_code
                        )
                return check

        else:

            @app_main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            def wrap2(
                context: Annotated[_T, fastapi.Depends(params[0])],
                request: Annotated[tuple[_U, bytes, bytes], fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal ret, check_version, xmc_verify
                check = client_check(context, check_version, xmc_verify)
                if check is None:
                    result: _V = f(context, request[0])  # type: ignore
                    # TODO: Response headers
                    return build_response(context, result)
                return check

        if batchable:
            if endpoint[0] == "/":
                module_action = endpoint[1:]
            else:
                module_action = endpoint
            API_ROUTER_MAP[module_action] = Endpoint(params[0], params[1] if len(params) > 1 else None, f)  # type: ignore
        return f

    return wrap0
