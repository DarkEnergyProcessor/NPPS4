import collections.abc
import functools

import pydantic

from . import item_model
from . import live_model
from . import scenario_model
from . import unit_model
from .. import idol
from .. import util

from typing import Callable, Hashable, cast


AnyItem = unit_model.AnyUnitItem | scenario_model.ScenarioItem | live_model.LiveItem | item_model.Item


class BeforeAfter[_T](pydantic.BaseModel):
    before: _T
    after: _T


class BaseRewardInfo(pydantic.BaseModel):
    game_coin: int
    game_coin_reward_box_flag: bool


class ItemCount(pydantic.BaseModel):
    item_id: int
    amount: int


class TimestampMixin(pydantic.BaseModel):
    server_timestamp: int = pydantic.Field(default_factory=util.time)


async def get_cached[
    T: Hashable, U
](
    context: idol.BasicSchoolIdolContext,
    key: str,
    id: T,
    miss: Callable[[idol.BasicSchoolIdolContext, T], collections.abc.Awaitable[U]],
    /,
):
    result: U | None = context.get_cache(key, id)

    if result is None:
        result = await miss(context, id)
        context.set_cache(key, id, result)

    return result


def context_cacheable(cache_key: str):
    """Decorator to allow caching result based on current idol context."""

    def wrap0[T: Hashable, U](f: Callable[[idol.BasicSchoolIdolContext, T], collections.abc.Awaitable[U]]):
        @functools.wraps(f)
        async def wrap(context: idol.BasicSchoolIdolContext, identifier: T, /):
            return await get_cached(context, cache_key, identifier, f)

        # In particular, Hashable and ParamSpec are umually exclusive. Making the type of "f" a generic that needs to
        # be said Callable is also not possible because Python doesn't allow nesting Generics. VSCode seems able to
        # preserve the type signature this way so ignore the errors for now.
        # Related: https://github.com/python/typeshed/issues/11280
        return cast(type(f), wrap)  # type: ignore

    return wrap0
