import urllib.parse

import fastapi

from . import database
from . import session
from .. import idoltype
from .. import util

from typing import Annotated, override


class BasicSchoolIdolContext:
    """Context object used only to access the database function."""

    def __init__(self, lang: idoltype.Language):
        self.lang = lang
        self.db = database.Database()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.db.commit()
        else:
            await self.db.rollback()
        await self.db.cleanup()

    def is_lang_jp(self):
        return self.lang == idoltype.Language.jp

    async def finalize(self):
        pass


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
        util.log(authorize)
        authorize_parsed = dict(urllib.parse.parse_qsl(authorize))
        if authorize_parsed.get("consumerKey") != "lovelive_test":
            raise fastapi.HTTPException(422, detail="Invalid consumerKey")

        cv_parsed = client_version.split(".", 1)
        try:
            self.client_version = (int(cv_parsed[0]), int(cv_parsed[1]))
        except ValueError as e:
            raise fastapi.HTTPException(422, detail=str(e)) from None

        try:
            self.nonce = int(authorize_parsed.get("nonce", 0))
        except ValueError:
            self.nonce = 0

        self.token_text = authorize_parsed.get("token")
        self.token: session.TokenData | None = None

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
        self.token_async = None
        if self.token_text is not None:
            self.token_async = session.decapsulate_token(self, self.token_text)

    @override
    async def finalize(self):
        if self.token_async is not None:
            self.token = await self.token_async
        if self.token is None:
            raise fastapi.HTTPException(403, detail="Invalid token")


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

    @override
    async def finalize(self):
        await super().finalize()
        assert self.token is not None
        if self.token.user_id == 0:
            raise fastapi.HTTPException(403, detail="Not logged in!")
