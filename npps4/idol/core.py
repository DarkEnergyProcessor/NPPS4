import dataclasses
import enum
import json
import typing
import urllib.parse

import fastapi
import pydantic
import sqlalchemy.ext.asyncio

from . import error
from .. import app
from .. import config
from .. import db
from .. import idoltype
from .. import release_key
from .. import util
from ..db import main
from ..db import game_mater
from ..db import item
from ..db import live
from ..db import unit

from typing import Annotated, Any, Callable, Coroutine, TypeVar, Generic


class DummyModel(pydantic.BaseModel):
    pass


class Database:
    def __init__(self) -> None:
        self._mainsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._gmsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._itemsession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._livesession: sqlalchemy.ext.asyncio.AsyncSession | None = None
        self._unitsession: sqlalchemy.ext.asyncio.AsyncSession | None = None

    @property
    def main(self):
        if self._mainsession is None:
            sessionmaker = main.get_sessionmaker()
            self._mainsession = sessionmaker()
        return self._mainsession

    @property
    def game_mater(self):
        if self._gmsession is None:
            self._gmsession = game_mater.get_session()
        return self._gmsession

    @property
    def item(self):
        if self._itemsession is None:
            self._itemsession = item.get_session()
        return self._itemsession

    @property
    def live(self):
        if self._livesession is None:
            self._livesession = live.get_session()
        return self._livesession

    @property
    def unit(self):
        if self._unitsession is None:
            self._unitsession = unit.get_session()
        return self._unitsession

    async def cleanup(self):
        if self._mainsession is not None:
            await self._mainsession.close()

    async def commit(self):
        if self._mainsession is not None:
            await self._mainsession.commit()

    async def rollback(self):
        if self._mainsession is not None:
            await self._mainsession.rollback()


class BasicSchoolIdolContext:
    """Context object used only to access the database function."""

    def __init__(self, lang: idoltype.Language):
        self.lang = lang
        self.db = Database()


class SchoolIdolParams(BasicSchoolIdolContext):
    """Context object used for unauthenticated request."""

    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[idoltype.Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[idoltype.PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True, include=False)] = None,
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

        ts = util.time()
        try:
            self.timestamp = int(authorize_parsed.get("timeStamp", ts))
        except ValueError:
            self.timestamp = ts
        self.platform = platform_type
        self.x_message_code = request.headers.get("X-Message-Code")
        self.request = request
        # Note: Due to how FastAPI works, the `request_data` form is retrieved TWICE!
        # One in here, retrieved as raw bytes, and the other one is in _get_request_data
        # as Pydantic model.
        # This is necessary for proper X-Message-Code verification!
        self.raw_request_data = request_data or b""

        super().__init__(lang)


class SchoolIdolAuthParams(SchoolIdolParams):
    """Context object used for initially authenticated request.

    Initially authenticated means there's no user associated with it.
    """

    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[idoltype.Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[idoltype.PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True, include=False)] = None,
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
        lang: Annotated[idoltype.Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[idoltype.PlatformType, fastapi.Header(alias="Platform-Type")],
        request_data: Annotated[bytes | None, fastapi.Form(exclude=True, include=False)] = None,
    ):
        super().__init__(request, authorize, client_version, lang, platform_type, request_data)
        if self.token.user_id == 0:
            raise fastapi.HTTPException(403, detail="Not logged in!")


_T = TypeVar("_T", bound=SchoolIdolParams)
_U = TypeVar("_U", bound=pydantic.BaseModel)
_V = TypeVar("_V", bound=pydantic.BaseModel, covariant=True)


_PossibleEndpointFunction = (
    Callable[[_T, _U], Coroutine[Any, Any, _V]]  # Request is pydantic, response is pydantic
    | Callable[[_T, list[_U]], Coroutine[Any, Any, _V]]  # Request is list of pydantics, response is pydantic
    | Callable[[_T, _U], Coroutine[Any, Any, list[_V]]]  # Request is pydantic, response is list of pydantics
    | Callable[
        [_T, list[_U]], Coroutine[Any, Any, list[_V]]
    ]  # Request is list of pydantics, response is list of pydantics
    | Callable[[_T], Coroutine[Any, Any, _V]]  # Request is none, response is pydantic
    | Callable[[_T], Coroutine[Any, Any, list[_V]]]  # Request is none, response is list of pydantics
)


@dataclasses.dataclass
class Endpoint(Generic[_T, _U, _V]):
    context_class: type[SchoolIdolParams | SchoolIdolAuthParams | SchoolIdolUserParams]
    request_class: type[pydantic.BaseModel] | None
    is_request_list: bool
    function: _PossibleEndpointFunction[_T, _U, _V]
    exclude_none: bool


def _get_request_data(model: type[_U]):
    def actual_getter(
        request_data: Annotated[pydantic.Json[model], fastapi.Form()],
        xmc: Annotated[str | None, fastapi.Header(alias="X-Message-Code")],
    ):
        return request_data

    return actual_getter


async def client_check(context: SchoolIdolParams, check_version: bool, xmc_verify: idoltype.XMCVerifyMode):
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
    if config.need_xmc_verify() and context.raw_request_data is not None and xmc_verify != idoltype.XMCVerifyMode.NONE:
        if context.x_message_code is None:
            raise fastapi.HTTPException(422, "Invalid X-Message-Code")
        if not isinstance(context, SchoolIdolAuthParams):
            raise fastapi.HTTPException(422, "Invalid X-Message-Code (no token)")

        if xmc_verify == idoltype.XMCVerifyMode.SHARED:
            hmac_key = util.xorbytes(context.token.client_key, context.token.server_key)
        elif xmc_verify == idoltype.XMCVerifyMode.CROSS:
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
            return await build_response(context, None)
    return None


_PossibleResponse = _V | list[_V] | error.IdolError | Exception | None


def assemble_response_data(response: _PossibleResponse[_V], exclude_none: bool = False):
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
        response_data = [r.model_dump(exclude_none=exclude_none) for r in response]
        status_code = http_code = 200
    else:
        response_data = response.model_dump(exclude_none=exclude_none)
        status_code = http_code = 200
    return response_data, status_code, http_code


async def build_response(
    context: SchoolIdolParams, response: _PossibleResponse[_V], log: bool = True, exclude_none: bool = False
):
    response_data_dict, status_code, http_code = assemble_response_data(response, exclude_none)
    response_data = {
        "response_data": response_data_dict,
        "release_info": release_key.formatted(),
        "status_code": status_code,
    }
    jsondatastr = json.dumps(response_data)
    jsondata = jsondatastr.encode("UTF-8")

    if config.log_request_response() and log:
        util.log("DEBUG RESPONSE", str(context.request.url), jsondatastr)

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


def _get_real_param(param: type[idoltype._S]):
    origin = typing.get_origin(param)

    if origin is list:
        return typing.get_args(param)[0], True
    else:
        return param, False


def _fix_schema(absdest: str, schema: dict[str, Any]):
    defs: dict[str, Any] | None = None

    if "$defs" in schema:
        if defs is None:
            defs = {}

        for k, v in schema["$defs"].items():
            defs[k] = v

    def replace(data: dict[str, Any] | list[Any]):
        nonlocal absdest

        i = None

        if isinstance(data, dict):
            if "$ref" in data:
                ref: str = data["$ref"]
                target = ref.split("/")[-1]
                data[
                    "$ref"
                ] = f"#/paths/{absdest.replace('~', '~0').replace('/', '~1')}/post/requestBody/$defs/{target}"

            i = data.values()
        elif isinstance(data, list):
            i = data

        for v in i:
            if isinstance(v, (dict, list)):
                replace(v)

    replace(schema)
    return defs, schema


API_ROUTER_MAP: dict[str, Endpoint] = {}
RESPONSE_HEADERS = {
    "Server-Version": {"type": "string"},
    "X-Message-Sign": {"type": "string"},
    "status_code": {"type": "string"},
}


def register(
    endpoint: str,
    *,
    check_version: bool = True,
    batchable: bool = True,
    xmc_verify: idoltype.XMCVerifyMode = idoltype.XMCVerifyMode.SHARED,
    exclude_none: bool = False,
):
    def wrap0(f: _PossibleEndpointFunction[_T, _U, _V]):
        nonlocal endpoint, check_version, batchable

        if endpoint[0] == "/":
            module_action = endpoint[1:]
        else:
            module_action = endpoint
        module_name = module_action.split("/")[0]

        signature = typing.get_type_hints(f)
        params = list(map(lambda x: x[1], filter(lambda x: x[0] != "return", signature.items())))
        ret: type[_V | pydantic.BaseModel] = signature.get("return", pydantic.BaseModel)
        tags: list[str | enum.Enum] = [module_name]

        if ret is pydantic.BaseModel:
            util.log("Possible undefined return type for endpoint:", endpoint, severity=util.logging.WARNING)
            ret = DummyModel

        if len(params) == 1:

            @app.main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=idoltype.ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
                tags=tags,
            )
            @app.main.get(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=idoltype.ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
                tags=tags,
            )
            async def wrap1(context: Annotated[_T, fastapi.Depends(params[0])]):
                nonlocal ret, check_version, xmc_verify, exclude_none
                response = await client_check(context, check_version, xmc_verify)
                if response is None:
                    try:
                        result: _V | list[_V] = await f(context)
                        await context.db.commit()
                        response = await build_response(context, result, exclude_none=exclude_none)
                    except error.IdolError as e:
                        await context.db.rollback()
                        response = await build_response(context, e)
                    except Exception:
                        await context.db.rollback()
                        raise
                    finally:
                        await context.db.cleanup()
                return response

        else:
            model = typing.cast(pydantic.BaseModel, params[1])
            schema = model.model_json_schema()
            print(endpoint, schema)

            # Fix schema
            defs, schema = _fix_schema("/main.php/" + module_action, schema)

            @app.main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=idoltype.ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
                tags=tags,
                response_model_exclude_none=exclude_none,
                openapi_extra={
                    "requestBody": {
                        "$defs": defs,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"request_data": schema},
                                    "required": ["request_data"],
                                }
                            },
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"request_data": schema},
                                    "required": ["request_data"],
                                }
                            },
                        },
                    },
                },
            )
            async def wrap2(
                context: Annotated[_T, fastapi.Depends(params[0])],
                request: Annotated[_U, fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal ret, check_version, xmc_verify
                response = await client_check(context, check_version, xmc_verify)
                if config.log_request_response():
                    util.log("DEBUG REQUEST", endpoint, str(context.raw_request_data, "UTF-8"))
                if response is None:
                    try:
                        result: _V | list[_V] = await f(context, request)
                        await context.db.commit()
                        response = await build_response(context, result, exclude_none=exclude_none)
                    except error.IdolError as e:
                        await context.db.rollback()
                        response = await build_response(context, e)
                    except Exception:
                        await context.db.rollback()
                        raise
                return response

        if batchable:
            real_request: type[_V] | None = None
            is_request_list = False

            if len(params) > 1:
                real_request, is_request_list = _get_real_param(params[1])

            API_ROUTER_MAP[module_action] = Endpoint(
                context_class=params[0],
                request_class=real_request,
                is_request_list=is_request_list,
                function=f,
                exclude_none=exclude_none,
            )
        return f

    return wrap0


class BatchRequest(pydantic.BaseModel):
    module: str
    action: str


class BatchRequestRoot(pydantic.RootModel):
    root: list[BatchRequest]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class BatchResponse(pydantic.BaseModel):
    result: dict | list
    status: int
    commandNum: bool = False
    timeStamp: int


class BatchResponseRoot(pydantic.RootModel):
    root: list[BatchResponse]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


_api_request_data_schema = {
    "type": "object",
    "properties": {"request_data": {"type": "array", "items": BatchRequest.model_json_schema()}},
    "required": ["request_data"],
}


@app.main.post(
    "/api",
    response_model=idoltype.ResponseData[BatchResponseRoot],
    openapi_extra={
        "requestBody": {
            "content": {
                "application/x-www-form-urlencoded": {"schema": _api_request_data_schema},
                "multipart/form-data": {"schema": _api_request_data_schema},
            }
        },
    },
)  # type: ignore
async def api_endpoint(
    context: Annotated[SchoolIdolUserParams, fastapi.Depends(SchoolIdolUserParams)],
    request: Annotated[list[BatchRequest], fastapi.Depends(_get_request_data(BatchRequestRoot))],
):
    response = await client_check(context, True, idoltype.XMCVerifyMode.SHARED)
    raw_request_data = json.loads(context.raw_request_data)

    if config.log_request_response():
        util.log("DEBUG REQUEST /api:", str(context.raw_request_data, "UTF-8"))

    if response is None:
        response_data: list[BatchResponse] = []

        for request_data in raw_request_data:
            module, action = request_data["module"], request_data["action"]

            try:
                # Find endpoint
                endpoint = API_ROUTER_MAP.get(f"{module}/{action}")
                if endpoint is None:
                    msg = f"Endpoint not found: {module}/{action}"
                    util.log(msg, json.dumps(request_data), severity=util.logging.ERROR)
                    raise error.IdolError(error.ERROR_CODE_LIB_ERROR, 404, msg, http_code=404)

                # *Sigh* have to reinvent the wheel.
                if endpoint.request_class is not None:
                    if endpoint.is_request_list:
                        pydantic_request = list(map(endpoint.request_class.model_validate, request_data))
                    else:
                        pydantic_request = endpoint.request_class.model_validate(request_data)
                    result = await endpoint.function(context, pydantic_request)  # type: ignore
                else:
                    result = await endpoint.function(context)  # type: ignore

                await context.db.commit()
                current_response, status_code, http_code = assemble_response_data(result, endpoint.exclude_none)
            except Exception as e:
                await context.db.rollback()

                if not isinstance(e, error.IdolError):
                    util.log(f'Error processing "{module}/{action}"', severity=util.logging.ERROR, e=e)

                current_response, status_code, http_code = assemble_response_data(e)

            response_data.append(BatchResponse(result=current_response, status=status_code, timeStamp=util.time()))

            if config.log_request_response():
                util.log("DEBUG REQUEST /api - ", module, action, ":::", json.dumps(request_data))
                util.log("DEBUG RESPONSE /api - ", module, action, ":::", json.dumps(current_response))

        response = await build_response(context, response_data, False)
    return response
