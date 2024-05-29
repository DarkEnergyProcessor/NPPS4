import base64
import dataclasses
import pickle
import urllib.parse

import fastapi
import itsdangerous
import sqlalchemy

from . import database
from . import session
from .. import idoltype
from .. import util
from ..config import config
from ..db import main

from typing import Annotated, Any, cast, overload, override


class BasicSchoolIdolContext:
    """Context object used only to access the database function."""

    def __init__(self, lang: idoltype.Language):
        self.lang = lang
        self.db = database.Database()
        self.cache: dict[str, dict[Any, Any]] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.db.commit()
        else:
            await self.db.rollback()
        await self.db.cleanup()
        self.cache = {}

    def is_lang_jp(self):
        return self.lang == idoltype.Language.jp

    @overload
    def get_text(self, text_jp: str, text_en: str | None) -> str: ...

    @overload
    def get_text(self, text_jp: str | None, text_en: str | None) -> str | None: ...

    def get_text(self, text_jp: str | None, text_en: str | None):
        if self.is_lang_jp():
            return text_jp
        else:
            return text_en if text_en is not None else text_jp

    async def finalize(self):
        pass

    def get_cache(self, key: str, id: Any):
        if key in self.cache and id in self.cache[key]:
            return self.cache[key][id]
        return None

    def set_cache(self, key: str, id: Any, value: Any):
        if key in self.cache:
            k: dict[Any, Any] = self.cache[key]
        else:
            k = {}
            self.cache[key] = k
        k[id] = value


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

    @override
    async def finalize(self):
        if self.token_text is not None:
            self.token = await session.decapsulate_token(self, self.token_text)
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


TOKEN_SERIALIZER = itsdangerous.serializer.Serializer(config.get_secret_key(), serializer=pickle)
FIRST_STAGE_TOKEN_MAX_DURATION = 60
SALT_SIZE = 16
TOKEN_SIZE = 16


@dataclasses.dataclass(kw_only=True)
class TokenData:
    client_key: bytes
    server_key: bytes
    user_id: int


async def encapsulate_token(context: BasicSchoolIdolContext, server_key: bytes, client_key: bytes, user_id: int = 0):
    salt = util.randbytes(SALT_SIZE)
    token = util.randbytes(TOKEN_SIZE).hex()[:TOKEN_SIZE]
    session = main.Session(
        token=token, user_id=None if user_id == 0 else user_id, client_key=client_key, server_key=server_key
    )
    result = cast(bytes, TOKEN_SERIALIZER.dumps(token, salt))

    context.db.main.add(session)
    await context.db.main.flush()
    return str(base64.urlsafe_b64encode(salt + result), "utf-8")


async def decapsulate_token(context: BasicSchoolIdolContext, token_data: str):
    t = util.time()

    # Delete unauthenticated tokens
    q = sqlalchemy.delete(main.Session).where(
        main.Session.user_id == None, main.Session.last_accessed < (t - FIRST_STAGE_TOKEN_MAX_DURATION)
    )
    await context.db.main.execute(q)
    await context.db.main.flush()

    # Delete tokens
    expiry_time = config.get_session_expiry_time()
    if expiry_time > 0:
        q = sqlalchemy.delete(main.Session).where(main.Session.last_accessed < (t - expiry_time))
        await context.db.main.execute(q)
        await context.db.main.flush()

    encoded_data = base64.urlsafe_b64decode(token_data)
    salt, result = encoded_data[:SALT_SIZE], encoded_data[SALT_SIZE:]
    try:
        token: str = TOKEN_SERIALIZER.loads(result, salt)
    except itsdangerous.BadSignature:
        return None

    q = sqlalchemy.select(main.Session).where(main.Session.token == token)
    result = await context.db.main.execute(q)
    session = result.scalar()
    if session is None:
        return None

    session.last_accessed = util.time()
    return TokenData(client_key=session.client_key, server_key=session.server_key, user_id=session.user_id or 0)


async def invalidate_current(context: SchoolIdolParams):
    if context.token_text is not None:
        q = sqlalchemy.delete(main.Session).where(main.Session.token == context.token_text)
        await context.db.main.execute(q)
        await context.db.main.flush()
