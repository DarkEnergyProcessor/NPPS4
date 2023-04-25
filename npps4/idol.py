import enum
import typing
import urllib.parse

import fastapi
import pydantic
import pydantic.generics

from .app import app_main

from typing import Annotated, Callable, Literal, TypeVar, Generic


class Language(str, enum.Enum):
    en = "en"
    jp = "jp"


class PlatformType(enum.IntEnum):
    iOS = 1
    Android = 2


class SchoolIdolParams:
    def __init__(
        self,
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
        self.token = authorize_parsed.get("token")
        self.lang: Literal["en", "jp"] = lang  # type: ignore
        self.platform: PlatformType = platform_type


class SchoolIdolAuthParams(SchoolIdolParams):
    def __init__(
        self,
        authorize: Annotated[str, fastapi.Header(alias="Authorize")],
        client_version: Annotated[str, fastapi.Header(alias="Client-Version")],
        lang: Annotated[Language, fastapi.Header(alias="LANG")],
        platform_type: Annotated[PlatformType, fastapi.Header(alias="Platform-Type")],
    ):
        super().__init__(authorize, client_version, lang, platform_type)
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


def _get_request_data(model: type[pydantic.BaseModel]):
    def actual_getter(
        request_data: Annotated[pydantic.Json[model], fastapi.Form()],
        xmc: Annotated[str, fastapi.Header(alias="X-Message-Code")],
    ):
        # TODO: verify xmc
        return request_data

    return actual_getter


def register(endpoint: str):
    def wrap0(f: Callable[[_T, _U], _V] | Callable[[_T], _V]):
        signature = typing.get_type_hints(f)
        params: list[type] = list(map(lambda x: x[1], filter(lambda x: x[0] != "return", signature.items())))
        ret: type[_V | pydantic.BaseModel] = signature.get("return", pydantic.BaseModel)

        if len(params) == 1:

            @app_main.post(endpoint, name=f.__name__, description=f.__doc__, response_model=ResponseData[ret])
            @app_main.get(endpoint, name=f.__name__, description=f.__doc__, response_model=ResponseData[ret])
            def wrap1(context: Annotated[_T, fastapi.Depends(params[0])]):
                nonlocal ret
                result: _V = f(context)
                return ResponseData[ret](response_data=result, release_info=[], status_code=200)

        else:

            @app_main.post(endpoint, name=f.__name__, description=f.__doc__, response_model=ResponseData[ret])
            def wrap2(
                context: Annotated[_T, fastapi.Depends(params[0])],
                request: Annotated[_U, fastapi.Depends(_get_request_data(params[1]))],
            ):
                nonlocal ret
                result: _V = f(context, request)
                return ResponseData[ret](response_data=result, release_info=[], status_code=200)

        return f

    return wrap0
