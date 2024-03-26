import fastapi

from . import error
from .core import register
from .session import BasicSchoolIdolContext, SchoolIdolParams, SchoolIdolAuthParams, SchoolIdolUserParams
from ..idoltype import Language, PlatformType, XMCVerifyMode


def create_basic_context(request: fastapi.Request):
    try:
        lang = Language(request.headers.get("LANG", "en"))
    except ValueError:
        lang = Language.en
    return BasicSchoolIdolContext(lang)
