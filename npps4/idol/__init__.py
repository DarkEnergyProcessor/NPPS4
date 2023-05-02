import enum
import dataclasses
import json
import time
import typing
import types
import urllib.parse

import fastapi
import pydantic
import pydantic.generics
import sqlalchemy.orm

from . import error
from .. import app
from .. import config
from .. import db
from .. import util

from typing import Annotated, Callable, TypeVar, Generic


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
        if self._mainsession is not None:
            self._mainsession.close()

    def commit(self):
        if self._mainsession is not None:
            self._mainsession.commit()

    def rollback(self):
        if self._mainsession is not None:
            self._mainsession.rollback()


class SchoolIdolParams:
    """Context object used for unauthenticated request."""

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

        # Note: Due to how FastAPI works, the `request_data` form is retrieved TWICE!
        # One in here, retrieved as raw bytes, and the other one is in _get_request_data
        # as Pydantic model.
        # This is necessary for proper X-Message-Code verification!
        self.raw_request_data = request_data
        self.lang: Language = lang
        self.platform: PlatformType = platform_type
        self.x_message_code = request.headers.get("X-Message-Code")
        self.request = request
        self.db = Database()


class SchoolIdolAuthParams(SchoolIdolParams):
    """Context object used for initially authenticated request.

    Initially authenticated means there's no user associated with it.
    """

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
    """Context object used for fully authenticated request.

    Fully authenticated means there's user associated with it.
    """

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


_S = TypeVar("_S", bound=pydantic.BaseModel | list[pydantic.BaseModel])


class ResponseData(pydantic.generics.GenericModel, Generic[_S]):
    response_data: _S
    release_info: list[config.ReleaseInfoData] = []
    status_code: int = 200


class ErrorResponse(pydantic.BaseModel):
    error_code: int
    detail: str | None


_T = TypeVar("_T", bound=SchoolIdolParams)
_U = TypeVar("_U", bound=pydantic.BaseModel)
_V = TypeVar("_V", bound=pydantic.BaseModel, covariant=True)


@dataclasses.dataclass
class Endpoint(Generic[_T, _U, _V]):
    context_class: type[SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams]
    request_class: type[pydantic.BaseModel] | None
    is_request_list: bool
    function: Callable[
        [SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams, pydantic.BaseModel | list[pydantic.BaseModel]],
        pydantic.BaseModel | list[pydantic.BaseModel],
    ] | Callable[
        [SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams], pydantic.BaseModel | list[pydantic.BaseModel]
    ]


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
            return build_response(context, None)
    return None


_PossibleResponse = pydantic.BaseModel | list[pydantic.BaseModel] | error.IdolError | Exception | None


def assemble_response_data(response: _PossibleResponse):
    if isinstance(response, error.IdolError):
        response_data = {"error_code": response.error_code, "detail": response.detail}
        status_code = response.status_code
        http_code = response.http_code
    elif isinstance(response, Exception):
        response_data = {
            "error_code": error.ERROR_CODE_LIB_ERROR,
            "detail": f"{type(response).__name__}: {str(response)}",
        }
        status_code = http_code = 500
    elif response is None:
        response_data = []
        status_code = http_code = 200
    elif isinstance(response, list):
        response_data = [r.dict() for r in response]
        status_code = http_code = 200
    else:
        response_data = response.dict()
        status_code = http_code = 200
    return response_data, status_code, http_code


def build_response(context: SchoolIdolParams, response: _PossibleResponse):
    from .. import download

    response_data_dict, status_code, http_code = assemble_response_data(response)
    response_data = {
        "response_data": response_data_dict,
        "release_info": download.get_formatted_release_keys(),
        "status_code": status_code,
    }
    jsondata = json.dumps(response_data).encode("UTF-8")
    context.db.cleanup()
    return fastapi.responses.Response(
        jsondata,
        http_code,
        {
            "Server-Version": util.sif_version_string(config.get_latest_version()),
            "X-Message-Sign": util.sign_message(jsondata, context.x_message_code),
            "status_code": str(status_code),
        },
        "application/json",
    )


def _get_real_param(param: type[_S]):
    if isinstance(param, types.GenericAlias) and param.__origin__ is list:
        return typing.get_args(param)[0], True
    else:
        return param, False


API_ROUTER_MAP: dict[str, Endpoint] = {}
RESPONSE_HEADERS = {
    "Server-Version": {"type": "string"},
    "X-Message-Sign": {"type": "string"},
    "status_code": {"type": "string"},
}


_PossibleEndpointFunction = (
    Callable[[_T, _U], _V]  # Request is pydantic, response is pydantic
    | Callable[[_T, list[_U]], _V]  # Request is list of pydantics, response is pydantic
    | Callable[[_T, _U], list[_V]]  # Request is pydantic, response is list of pydantics
    | Callable[[_T, list[_U]], list[_V]]  # Request is list of pydantics, response is list of pydantics
    | Callable[[_T], _V]  # Request is none, response is pydantic
    | Callable[[_T], list[_V]]  # Request is none, response is list of pydantics
)


def register(
    endpoint: str,
    *,
    check_version: bool = True,
    batchable: bool = True,
    xmc_verify: XMCVerifyMode = XMCVerifyMode.SHARED,
):
    def wrap0(f: _PossibleEndpointFunction[_T, _U, _V]):
        nonlocal endpoint, check_version, batchable

        signature = typing.get_type_hints(f)
        params: list[type] = list(map(lambda x: x[1], filter(lambda x: x[0] != "return", signature.items())))
        ret: type[_V | pydantic.BaseModel] = signature.get("return", pydantic.BaseModel)

        if ret is pydantic.BaseModel:
            util.log("Possible undefined return type for endpoint:", endpoint, severity=util.logging.WARNING)

        if len(params) == 1:

            @app.main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            @app.main.get(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            def wrap1(context: Annotated[_T, fastapi.Depends(params[0])]):
                nonlocal ret, check_version, xmc_verify
                response = client_check(context, check_version, xmc_verify)
                if response is None:
                    try:
                        result: _V = f(context)  # type: ignore
                        context.db.commit()
                        response = build_response(context, result)
                    except error.IdolError as e:
                        context.db.rollback()
                        response = build_response(context, e)
                    except Exception:
                        context.db.rollback()
                        raise
                return response

        else:

            @app.main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
            )
            def wrap2(
                context: Annotated[_T, fastapi.Depends(params[0])],
                request: Annotated[_U, fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal ret, check_version, xmc_verify
                response = client_check(context, check_version, xmc_verify)
                if response is None:
                    try:
                        result: _V = f(context, request)  # type: ignore
                        context.db.commit()
                        response = build_response(context, result)
                    except error.IdolError as e:
                        context.db.rollback()
                        response = build_response(context, e)
                    except Exception:
                        context.db.rollback()
                        raise
                return response

        if batchable:
            if endpoint[0] == "/":
                module_action = endpoint[1:]
            else:
                module_action = endpoint

            if len(params) > 1:
                real_request, is_request_list = _get_real_param(params[1])
            else:
                real_request, is_request_list = None, False
            API_ROUTER_MAP[module_action] = Endpoint(
                context_class=params[0],
                request_class=real_request,  # type: ignore
                is_request_list=is_request_list,
                function=f,  # type: ignore
            )
        return f

    return wrap0


class BatchRequest(pydantic.BaseModel):
    module: str
    action: str


class BatchResponse(pydantic.BaseModel):
    result: dict | list
    status: int
    commandNum: bool = False
    timeStamp: int


@app.main.post("/api", response_model=ResponseData[list[BatchResponse]])  # type: ignore
def api_endpoint(
    context: Annotated[SchoolIdolUserParams, fastapi.Depends(SchoolIdolUserParams)],
    request: Annotated[list[BatchRequest], fastapi.Depends(_get_request_data(list[BatchRequest]))],  # type: ignore
    raw_request_data: Annotated[list[dict[str, object]], fastapi.Form(alias="request_data", exclude=True)],
):
    response = client_check(context, True, XMCVerifyMode.SHARED)

    if response is None:
        response_data: list[BatchResponse] = []

        for request_data in raw_request_data:
            module, action = request_data["module"], request_data["action"]

            try:
                # Find endpoint
                endpoint = API_ROUTER_MAP.get(f"{module}/{action}")
                if endpoint is None:
                    raise error.IdolError(error.ERROR_CODE_LIB_ERROR, 404, http_code=404)

                # *Sigh* have to reinvent the wheel.
                if endpoint.request_class is not None:
                    if endpoint.is_request_list:
                        pydantic_request = list(map(endpoint.request_class.parse_obj, request_data))
                    else:
                        pydantic_request = endpoint.request_class.parse_obj(request_data)
                    result = endpoint.function(context, pydantic_request)  # type: ignore
                else:
                    result = endpoint.function(context)  # type: ignore

                context.db.commit()
                current_response, status_code, http_code = assemble_response_data(result)
            except Exception as e:
                context.db.rollback()
                if not isinstance(e, error.IdolError):
                    util.log(f'Error processing "{module}/{action}"', severity=util.logging.ERROR, e=e)
                current_response, status_code, http_code = assemble_response_data(e)

            response_data.append(BatchResponse(result=current_response, status=status_code, timeStamp=util.time()))

        response = build_response(context, response_data)  # type: ignore
    return response
