import cProfile
import collections.abc
import dataclasses
import enum
import gzip
import json
import os
import os.path
import time
import traceback
import typing

import fastapi
import pydantic

from . import cache
from . import session
from . import error
from .. import idoltype
from .. import release_key
from .. import util
from ..app import app
from ..config import config

from typing import Annotated, Any, Callable, TypeVar, Generic, cast


class DummyModel(pydantic.RootModel[list]):
    root: list = pydantic.Field(default_factory=list)


_T = TypeVar("_T", bound=session.SchoolIdolParams)
_U = TypeVar("_U", bound=pydantic.BaseModel)
_V = TypeVar("_V", bound=pydantic.BaseModel, covariant=True)

_EndpointWithRequestWithResponse = Callable[
    [_T, _U], collections.abc.Awaitable[_V]
]  # Request is pydantic, response is pydantic
_EndpointWithoutRequestWithResponse = Callable[
    [_T], collections.abc.Awaitable[_V]
]  # Request is none, response is pydantic
_EndpointWithRequestWithoutResponse = Callable[
    [_T, _U], collections.abc.Awaitable[None]
]  # Request is pydantic, response is none
_EndpointWithoutRequestWithoutResponse = Callable[
    [_T], collections.abc.Awaitable[None]
]  # Request is none, response is none
_PossibleEndpointFunction = (
    _EndpointWithoutRequestWithResponse[_T, _V]
    | _EndpointWithRequestWithResponse[_T, _U, _V]
    | _EndpointWithRequestWithoutResponse[_T, _U]
    | _EndpointWithoutRequestWithoutResponse[_T]
)


@dataclasses.dataclass
class Endpoint(Generic[_T, _U, _V]):
    context_class: type[_T]
    request_class: type[pydantic.BaseModel] | None
    function: _PossibleEndpointFunction[_T, _U, _V]
    exclude_none: bool
    log_response_data: bool
    profile: bool


def _get_request_data[U: pydantic.BaseModel](model: type[U]):
    def actual_getter(
        request_data: Annotated[pydantic.Json, fastapi.Form()],
        xmc: Annotated[str | None, fastapi.Header(alias="X-Message-Code")],
    ):
        return model.model_validate(request_data)

    return actual_getter


async def client_check(context: session.SchoolIdolParams, check_version: bool, xmc_verify: idoltype.XMCVerifyMode):
    # Maintenance check
    if config.is_maintenance():
        return fastapi.responses.JSONResponse(
            [],
            200,
            {
                "Maintenance": "1",
            },
        )

    # Only for /login/authkey.
    if xmc_verify != idoltype.XMCVerifyMode.NONE and context.token is None:
        raise fastapi.HTTPException(403, detail="Invalid token")

    # XMC check
    if config.need_xmc_verify() and context.raw_request_data is not None and xmc_verify != idoltype.XMCVerifyMode.NONE:
        assert context.token is not None

        if context.x_message_code is None:
            raise fastapi.HTTPException(422, "Invalid X-Message-Code")
        if not isinstance(context, session.SchoolIdolAuthParams):
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
    context: session.SchoolIdolParams, response: _PossibleResponse[_V] | bytes, exclude_none: bool = False
):
    if isinstance(response, bytes):
        http_code = 200
        status_code = 200
    else:
        response_data_dict, status_code, http_code = assemble_response_data(
            cast(_PossibleResponse[_V], response), exclude_none
        )
        response_data = {
            "response_data": response_data_dict,
            "release_info": release_key.formatted(),
            "status_code": status_code,
        }
        jsondatastr = json.dumps(response_data)
        response = jsondatastr.encode("UTF-8")

    response_headers = {
        "Server-Version": util.sif_version_string(config.get_latest_version()),
        "X-Message-Sign": util.sign_message(response, context.x_message_code),
        "status_code": str(status_code),
    }

    allow_compress = "gzip" in context.request.headers.get("accept-encoding", "identity").lower()
    if allow_compress and len(response) >= 65536:
        # GZip compress
        response = gzip.compress(response)
        response_headers["Content-Encoding"] = "gzip"

    return fastapi.responses.Response(
        response,
        http_code,
        response_headers,
        "application/json",
    )


def _log_response_data(module: str, action: str, response_data: pydantic.BaseModel):
    output_dir = os.path.join(config.get_data_directory(), "log_response_data")
    os.makedirs(output_dir, exist_ok=True)
    t = time.time_ns()
    filename = f"{module}_{action}_{t:08x}.json"

    with open(os.path.join(output_dir, filename), "w", encoding="utf-8", newline="\n") as f:
        jsonable = response_data.model_dump()
        json.dump(jsonable, f, ensure_ascii=False, indent="\t")

    util.log(f"Response data for {module}/{action} is saved to {filename}", severity=util.logging.DEBUG)


def _write_profile_data(module: str, action: str, prof: cProfile.Profile):
    output_dir = os.path.join(config.get_data_directory(), "profile_endpoint")
    os.makedirs(output_dir, exist_ok=True)
    t = util.time()
    filename = f"{module}_{action}_{t:08x}.prof"

    try:
        prof.dump_stats(os.path.join(output_dir, filename))
        util.log(f"Profile result for {module}/{action} is saved to {filename}", severity=util.logging.DEBUG)
    except OSError as e:
        util.log(f"Unable to save profile result for {module}/{action} to {filename}", e=e, severity=util.logging.DEBUG)


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
                data["$ref"] = (
                    f"#/paths/{absdest.replace('~', '~0').replace('/', '~1')}/post/requestBody/$defs/{target}"
                )

            i = data.values()
        elif isinstance(data, list):
            i = data

        for v in i:
            if isinstance(v, (dict, list)):
                replace(v)

    replace(schema)
    return defs, schema


API_ROUTER_MAP: dict[tuple[str, str], Endpoint] = {}
RESPONSE_HEADERS = {
    "Server-Version": {"type": "string"},
    "X-Message-Sign": {"type": "string"},
    "status_code": {"type": "string"},
}


def _exception_traceback_to_str(exc: Exception):
    tb = traceback.format_exception(exc)
    return "\n".join(tb)


def register(
    module: str,
    action: str,
    *,
    check_version: bool = True,
    batchable: bool = True,
    xmc_verify: idoltype.XMCVerifyMode = idoltype.XMCVerifyMode.SHARED,
    exclude_none: bool = False,
    # These are only for debug purpose.
    log_response_data: bool = False,
    allow_retry_on_unhandled_exception: bool = False,
    profile_this_endpoint: bool = False,
):
    if (module, action) in API_ROUTER_MAP:
        raise ValueError(f"Endpoint {module}/{action} is already registered!")

    def wrap0(f: _PossibleEndpointFunction[_T, _U, _V]):
        nonlocal batchable, log_response_data, profile_this_endpoint

        if config.is_script_mode():
            # Do nothing when in script mode
            return f

        endpoint = f"/{module}/{action}"
        signature = typing.get_type_hints(f)
        params = list(map(lambda x: x[1], filter(lambda x: x[0] != "return", signature.items())))
        ret: type[_V | pydantic.BaseModel | None] = signature.get("return", pydantic.BaseModel)
        tags: list[str | enum.Enum] = [module]

        if ret is pydantic.BaseModel:
            util.log("Possible undefined return type for endpoint:", endpoint, severity=util.logging.WARNING)
            ret = DummyModel
        elif ret is type(None):
            ret = DummyModel

        if len(params) == 1:

            async def wrap1(context: Annotated[_T, fastapi.Depends(params[0])]):
                nonlocal check_version, xmc_verify, exclude_none, f, allow_retry_on_unhandled_exception
                nonlocal log_response_data, profile_this_endpoint, endpoint
                func = cast(_EndpointWithoutRequestWithResponse[_T, _V] | _EndpointWithoutRequestWithoutResponse[_T], f)

                async with context:
                    await context.finalize()

                response = await client_check(context, check_version, xmc_verify)
                if response is None:
                    try:
                        async with context:
                            cached_response = await cache.load_response(context, endpoint)

                            if cached_response is None:
                                if profile_this_endpoint:
                                    profile_obj = cProfile.Profile()
                                    with profile_obj:
                                        result = await func(context)
                                    _write_profile_data(module, action, profile_obj)
                                else:
                                    result = await func(context)
                                response = await build_response(context, result, exclude_none=exclude_none)
                                await cache.store_response(context, endpoint, response.body)

                                if log_response_data and result is not None:
                                    _log_response_data(module, action, result)
                            else:
                                response = await build_response(context, cached_response)
                    except error.IdolError as e:
                        response = await build_response(context, e)
                    except Exception as e:
                        if allow_retry_on_unhandled_exception:
                            response = await build_response(
                                context, error.IdolError(detail=_exception_traceback_to_str(e))
                            )
                        else:
                            raise e from None
                return response

            app.main.post(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=idoltype.ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
                response_model_exclude_none=exclude_none,
                tags=tags,
            )(wrap1)
            app.main.get(
                endpoint,
                name=f.__name__,
                description=f.__doc__,
                response_model=idoltype.ResponseData[ret],
                responses={200: {"headers": RESPONSE_HEADERS}},
                response_model_exclude_none=exclude_none,
                tags=tags,
            )(wrap1)
        else:
            model = typing.cast(pydantic.BaseModel, params[1])
            schema = model.model_json_schema()

            # Fix schema
            defs, schema = _fix_schema("/main.php" + endpoint, schema)

            async def wrap2(
                context: Annotated[_T, fastapi.Depends(params[0])],
                request: Annotated[_U, fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal check_version, xmc_verify, f, allow_retry_on_unhandled_exception, log_response_data
                nonlocal profile_this_endpoint, endpoint

                async with context:
                    await context.finalize()

                func = cast(_EndpointWithRequestWithResponse[_T, _U, _V], f)
                response = await client_check(context, check_version, xmc_verify)

                if response is None:
                    try:
                        async with context:
                            cached_response = await cache.load_response(context, endpoint)

                            if cached_response is None:
                                if profile_this_endpoint:
                                    profile_obj = cProfile.Profile()
                                    with profile_obj:
                                        result = await func(context, request)
                                    _write_profile_data(module, action, profile_obj)
                                else:
                                    result = await func(context, request)
                                response = await build_response(context, result, exclude_none=exclude_none)
                                await cache.store_response(context, endpoint, response.body)

                                if log_response_data and result is not None:
                                    _log_response_data(module, action, result)
                            else:
                                result = await build_response(context, cached_response, exclude_none=exclude_none)
                    except error.IdolError as e:
                        response = await build_response(context, e)
                    except Exception as e:
                        if allow_retry_on_unhandled_exception:
                            traceback.print_exception(e)
                            response = await build_response(
                                context, error.IdolError(detail=_exception_traceback_to_str(e))
                            )
                        else:
                            raise e from None
                return response

            app.main.post(
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
            )(wrap2)
        if batchable and xmc_verify != idoltype.XMCVerifyMode.CROSS:
            API_ROUTER_MAP[(module, action)] = Endpoint(
                context_class=params[0],
                request_class=None if len(params) < 2 else params[1],
                function=f,
                exclude_none=exclude_none,
                log_response_data=log_response_data,
                profile=profile_this_endpoint,
            )
        return f

    return wrap0


class BatchRequest(pydantic.BaseModel):
    module: str
    action: str


class BatchRequestRoot(pydantic.RootModel):
    root: list[BatchRequest]


class BatchResponse(pydantic.BaseModel):
    result: dict | list
    status: int
    commandNum: bool = False
    timeStamp: int


class BatchResponseRoot(pydantic.RootModel):
    root: list[BatchResponse]


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
)
async def api_endpoint(
    context: Annotated[session.SchoolIdolUserParams, fastapi.Depends(session.SchoolIdolUserParams)],
    request: Annotated[list[BatchRequest], fastapi.Depends(_get_request_data(BatchRequestRoot))],
):
    async with context:
        await context.finalize()

    response = await client_check(context, True, idoltype.XMCVerifyMode.SHARED)
    raw_request_data = json.loads(context.raw_request_data)

    if response is None:
        endpoint_name_list = ["/api"]

        for request_data in raw_request_data:
            endpoint_name_list.append(request_data["module"])
            endpoint_name_list.append(request_data["action"])

        endpoint_name = "_".join(endpoint_name_list)
        async with context:
            cached_response = await cache.load_response(context, endpoint_name)

            if cached_response is None:
                response_data: list[BatchResponse] = []

                for request_data in raw_request_data:
                    module, action = request_data["module"], request_data["action"]

                    try:
                        # Find endpoint
                        endpoint = API_ROUTER_MAP.get((module, action))
                        if endpoint is None:
                            msg = f"Endpoint not found: {module}/{action}"
                            util.log(msg, json.dumps(request_data), severity=util.logging.ERROR)
                            raise error.IdolError(error.ERROR_CODE_LIB_ERROR, 404, msg, http_code=404)

                        # *Sigh* have to reinvent the wheel.
                        if endpoint.request_class is not None:
                            pydantic_request = endpoint.request_class.model_validate(request_data)
                            func = cast(
                                _EndpointWithRequestWithResponse[
                                    session.SchoolIdolUserParams, pydantic.BaseModel, pydantic.BaseModel
                                ]
                                | _EndpointWithRequestWithoutResponse[session.SchoolIdolUserParams, pydantic.BaseModel],
                                endpoint.function,
                            )

                            if endpoint.profile:
                                profile_obj = cProfile.Profile()
                                with profile_obj:
                                    result = await func(context, pydantic_request)
                                _write_profile_data(module, action, profile_obj)
                            else:
                                result = await func(context, pydantic_request)
                        else:
                            func = cast(
                                _EndpointWithoutRequestWithResponse[session.SchoolIdolUserParams, pydantic.BaseModel]
                                | _EndpointWithoutRequestWithoutResponse[session.SchoolIdolUserParams],
                                endpoint.function,
                            )
                            if endpoint.profile:
                                profile_obj = cProfile.Profile()
                                with profile_obj:
                                    result = await func(context)
                                _write_profile_data(module, action, profile_obj)
                            else:
                                result = await func(context)

                        if endpoint.log_response_data and result is not None:
                            _log_response_data(module, action, result)

                        current_response, status_code, http_code = assemble_response_data(result, endpoint.exclude_none)
                    except Exception as e:
                        if not isinstance(e, error.IdolError):
                            util.log(f'Error processing "{module}/{action}"', severity=util.logging.ERROR, e=e)

                        current_response, status_code, http_code = assemble_response_data(e)

                    response_data.append(
                        BatchResponse(result=current_response, status=status_code, timeStamp=util.time())
                    )

                response = await build_response(context, response_data, False)
                await cache.store_response(context, endpoint_name, response.body)
            else:
                response = await build_response(context, cached_response)
    return response
