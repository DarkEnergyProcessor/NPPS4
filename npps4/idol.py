import enum
import dataclasses
import json
import time
import typing
import urllib.parse

import fastapi
import pydantic
import pydantic.generics

from .app import app_main
from . import config
from . import util

from typing import Annotated, Callable, TypeVar, Generic


class Language(str, enum.Enum):
    en = "en"
    jp = "jp"


class PlatformType(enum.IntEnum):
    iOS = 1
    Android = 2


class SchoolIdolParams:
    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
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


class SchoolIdolAuthParams(SchoolIdolParams):
    def __init__(
        self,
        request: fastapi.Request,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
    ):
        super().__init__(request, authorize, client_version, lang, platform_type)
        self.token: util.TokenData | None = None
        if self.token_text is not None:
            self.token = util.decapsulate_token(self.token_text)

        if self.token is None:
            raise fastapi.HTTPException(422, detail="Invalid token")


class ReleaseInfoData(pydantic.BaseModel):
    id: int
    key: str


_S = TypeVar("_S", bound=pydantic.BaseModel)


class ResponseData(pydantic.generics.GenericModel, Generic[_S]):
    response_data: _S
    release_info: list[ReleaseInfoData] = []
    status_code: int = 200


_T = TypeVar("_T", bound=SchoolIdolParams)
_U = TypeVar("_U", bound=pydantic.BaseModel)
_V = TypeVar("_V", bound=pydantic.BaseModel)


@dataclasses.dataclass
class Endpoint(Generic[_T, _U, _V]):
    context_class: type[SchoolIdolParams | SchoolIdolAuthParams]
    request_class: type[pydantic.BaseModel] | None
    function: Callable[[SchoolIdolParams | SchoolIdolAuthParams, pydantic.BaseModel], pydantic.BaseModel] | Callable[
        [SchoolIdolParams | SchoolIdolAuthParams], pydantic.BaseModel
    ]


def _get_request_data(model: type[pydantic.BaseModel]):
    def actual_getter(
        request_data: Annotated[pydantic.Json[model], fastapi.Form()],
        xmc: Annotated[str, fastapi.Header(alias="X-Message-Code")],
    ):
        # TODO: verify xmc
        return request_data, xmc

    return actual_getter


def client_check(context: SchoolIdolParams, check_version: bool = True):
    if config.is_maintenance():
        return fastapi.responses.JSONResponse(
            [],
            200,
            {
                "Maintenance": "1",
            },
        )
    if check_version:
        if config.get_latest_version() != context.client_version:
            return fastapi.responses.JSONResponse([], 200)
    return None


def build_response(context: SchoolIdolParams, response: pydantic.BaseModel):
    response_data = {"response_data": response.dict(), "release_info": [], "status_code": 200}  # TODO
    jsondata = json.dumps(response_data).encode("UTF-8")
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


def register(endpoint: str, *, check_version: bool = True, batchable: bool = True):
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
                nonlocal ret, check_version
                check = client_check(context, check_version)
                if check is None:
                    result: _V = f(context)  # type: ignore
                    # TODO: Response headers
                    return build_response(context, result)
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
                request: Annotated[tuple[_U, bytes], fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal ret, check_version
                check = client_check(context, check_version)
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
