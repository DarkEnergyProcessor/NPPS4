import re

from .. import idol
from ..db import game_mater

from typing import Any, Callable, overload

_SERVER_STINGS: list[tuple[int, str, str | None]] = [
    # When adding new strings, please put the index (0-based) and append them!
    # FIXME: Proper EN translation.
    (0, "Rankを%d にしよう!の報酬", "Let's make the Rank %d!"),
    (1, "ライプの報醂", "Live Show Reward"),
]
_ss = dict((k[0], (k[1], k[2])) for k in _SERVER_STINGS)
SERVER_STRINGS = [_ss.get(k, ("", None)) for k in range(max(_ss.keys()) + 1)]


@overload
def get(string_key: str, string_value: int | str, context: idol.Language | idol.BasicSchoolIdolContext) -> str:
    ...


@overload
def get(string_key: str, string_value: int | str) -> tuple[str, str | None]:
    ...


def get(string_key: str, string_value: int | str, context: idol.Language | idol.BasicSchoolIdolContext | None = None):
    string = game_mater.STRINGS[string_key, str(string_value)]

    if context is not None:
        return select(string, context)
    else:
        return string


def select(string: tuple[str, str | None], context: idol.Language | idol.BasicSchoolIdolContext):
    match context:
        case idol.Language():
            lang = context
        case idol.BasicSchoolIdolContext():
            lang = context.lang
        case _:
            raise TypeError("expected Language or BasicSchoolIdolContext")

    return string[1 if lang == idol.Language.en else 0] or string[0]


MAPPED_MATCH = re.compile(r"\{\{([a-zA-Z0-9_])\}\}")
POSITIONAL_MATCH = re.compile(r"%[[\d]+\$]*[a-z]")


def format_mapped(string: str, /, **kwargs: int | str):
    def repl(m: re.Match[str]):
        nonlocal kwargs
        value = kwargs.get(m.group(1), "{{" + m.group() + "}}")
        return str(value)

    return re.sub(MAPPED_MATCH, repl, string)


_FMT_SPECIFIER: dict[str, tuple[type, Callable[[Any], str]]] = {
    "s": (str, str),
    "d": (int, str),
    "x": (int, lambda k: str.format("%x", k)),
}


def format_positional(string: str, /, *args: int | str):
    index_counter = 1

    def repl(m: re.Match[str]):
        nonlocal index_counter, args
        fmt = m.group()
        dollar = fmt.find("$")
        if dollar > 0:
            pos = int(fmt[1:dollar])
        else:
            pos = index_counter
            index_counter = index_counter + 1

        value = args[pos - 1]

        try:
            fmt_specifier = _FMT_SPECIFIER[fmt[-1]]
            if type(value) is not fmt_specifier[0]:
                raise ValueError(f"invalid format specifier index {pos}")
        except KeyError as e:
            raise ValueError(f"unknown format specifier '{fmt[-1]}'") from e

        return fmt_specifier[1](value)

    return re.sub(POSITIONAL_MATCH, repl, string)
