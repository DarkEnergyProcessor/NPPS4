import pydantic

from . import common
from . import item
from . import item_model
from .. import const
from .. import idol
from ..config import config
from ..db import main
from ..db import effort


class EffortPointInfo(common.BeforeAfter[int]):
    live_effort_point_box_spec_id: int
    capacity: int
    rewards: list[item_model.Item]


async def get_effort_spec(context: idol.BasicSchoolIdolContext, live_effort_point_box_spec_id: int):
    effort_spec = await context.db.effort.get(effort.LiveEffortPointBoxSpec, live_effort_point_box_spec_id)
    if effort_spec is None:
        raise ValueError(f"invalid live_effort_point_box_spec_id {live_effort_point_box_spec_id}")

    return effort_spec


async def add_effort(context: idol.BasicSchoolIdolContext, user: main.User, amount: int):
    result: list[EffortPointInfo] = []
    live_box_drop_protocol = config.get_live_box_drop_protocol()
    current_amount = amount
    offer_limited_box_id = 0

    # TODO: Properly handle limited effort box
    while True:
        is_limited = user.limited_effort_event_id > 0
        effort_spec = await get_effort_spec(context, user.live_effort_point_box_spec_id)
        capacity = effort_spec.limited_capacity if is_limited else effort_spec.capacity
        oldvalue = user.current_limited_effort_point if is_limited else user.current_live_effort_point
        newvalue = min(oldvalue + current_amount, capacity)
        addedvalue = newvalue - oldvalue
        current_amount = current_amount - addedvalue

        if is_limited:
            user.current_limited_effort_point = newvalue
        else:
            user.current_live_effort_point = newvalue

        if newvalue >= capacity:
            # Give reward
            drop_box_result = await live_box_drop_protocol.process_effort_box(
                context, user.live_effort_point_box_spec_id, user.limited_effort_event_id, amount
            )

            reward_list: list[item_model.Item] = []
            for add_type, item_id, item_count, additional_data in drop_box_result.rewards:
                reward_data = item_model.Item(add_type=const.ADD_TYPE(add_type), item_id=item_id, amount=item_count)
                if additional_data:
                    for k, v in additional_data.items():
                        setattr(reward_data, k, v)

                await item.update_item_category_id(context, reward_data)
                reward_list.append(reward_data)

            # FIXME: This does NOT handle limited effort box properly!
            result.append(
                EffortPointInfo(
                    live_effort_point_box_spec_id=user.live_effort_point_box_spec_id,
                    capacity=effort_spec.capacity,
                    before=oldvalue,
                    after=newvalue,
                    rewards=reward_list,
                )
            )

            if is_limited:
                user.limited_effort_event_id = 0
                user.current_limited_effort_point = 0
            else:
                user.live_effort_point_box_spec_id = drop_box_result.new_live_effort_point_box_spec_id
                user.current_live_effort_point = 0

            if drop_box_result.offer_limited_effort_event_id > 0:
                offer_limited_box_id = drop_box_result.offer_limited_effort_event_id

        if current_amount <= 0:
            break

    result.append(
        EffortPointInfo(
            live_effort_point_box_spec_id=user.live_effort_point_box_spec_id,
            capacity=effort_spec.capacity,
            before=oldvalue,
            after=user.current_live_effort_point,
            rewards=[],
        )
    )
    await context.db.main.flush()
    return result, offer_limited_box_id
