import collections.abc

import sqlalchemy

from .. import idol
from .. import util
from ..data import schema
from ..db import main
from ..system import advanced
from ..system import reward

from typing import Callable

functions: dict[str, Callable[[idol.BasicSchoolIdolContext, main.User], collections.abc.Awaitable[str | None]]] = {}


async def execute(
    context: idol.BasicSchoolIdolContext, user: main.User, /, input_code: str, serial_code: schema.SerialCode
):
    # Check amount
    serial_code_tracker = None
    if serial_code.usage_limit is not None:
        serial_code_id = util.java_hash_code(serial_code.usage_limit.id, 0x7FFFFFFFFFFFFFFF)
        if serial_code.usage_limit.global_:
            q = sqlalchemy.select(main.GlobalSerialCodeUsage).where(
                main.GlobalSerialCodeUsage.serial_code_id == serial_code_id
            )
            result = await context.db.main.execute(q)
            serial_code_tracker = result.scalar()

            if serial_code_tracker is None:
                serial_code_tracker = main.GlobalSerialCodeUsage(serial_code_id=serial_code_id, count=0)
                context.db.main.add(serial_code_tracker)
        else:
            q = sqlalchemy.select(main.LocalSerialCodeUsage).where(
                main.LocalSerialCodeUsage.user_id == user.id, main.LocalSerialCodeUsage.serial_code_id == serial_code_id
            )
            result = await context.db.main.execute(q)
            serial_code_tracker = result.scalar()

            if serial_code_tracker is None:
                serial_code_tracker = main.LocalSerialCodeUsage(user_id=user.id, serial_code_id=serial_code_id, count=0)
                context.db.main.add(serial_code_tracker)

        if serial_code_tracker.count >= serial_code.usage_limit.amount:
            raise ValueError("serial code usage exceeded")

    action = serial_code.get_action(input_code)
    result_str = None
    match action:
        case schema.SerialCodeGiveItem():
            given_item: list[str] = ["Successfully given these items:"]
            for item_data_serialized in action.items:
                item_data = await advanced.deserialize_item_data(context, item_data_serialized)
                await reward.add_item(context, user, item_data, action.message_jp, action.message_en)
                given_item.append(f"{item_data.amount}x {await advanced.get_item_name(context, item_data)}")

            result_str = "\n".join(given_item)
        case schema.SerialCodeRunFunction():
            if action.function not in functions:
                if isinstance(serial_code.action, list):
                    raise ValueError("cannot find specified function")
                else:
                    raise ValueError(f"cannot find '{action.function}' function")

            result_str = (await functions[action.function](context, user)) or "Serial code successfully executed."
        case _:
            raise TypeError("internal error")

    if serial_code_tracker is not None:
        serial_code_tracker.count = serial_code_tracker.count + 1
        await context.db.main.flush()

    return result_str
