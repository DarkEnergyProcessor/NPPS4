import pydantic

from . import common
from . import item
from ... import idol
from ...config import config
from ...db import main
from ...db import effort


class EffortReward(item.RewardWithCategory):
    rarity: int = 6  # TODO


class EffortPointInfo(common.BeforeAfter[int]):
    live_effort_point_box_spec_id: int
    capacity: int
    rewards: list[EffortReward]


async def get_effort_spec(context: idol.BasicSchoolIdolContext, live_effort_point_box_spec_id: int):
    effort_spec = await context.db.effort.get(effort.LiveEffortPointBoxSpec, live_effort_point_box_spec_id)
    if effort_spec is None:
        raise ValueError(f"invalid live_effort_point_box_spec_id {live_effort_point_box_spec_id}")

    return effort_spec


async def get_effort_data(context: idol.BasicSchoolIdolContext, user: main.User):
    live_effort = await context.db.main.get(main.LiveEffort, user.id)
    if live_effort is None:
        live_effort = main.LiveEffort(user_id=user.id)
        context.db.main.add(live_effort)
        await context.db.main.flush()

    return live_effort


async def add_effort(context: idol.BasicSchoolIdolContext, user: main.User, amount: int):
    result: list[EffortPointInfo] = []
    current_effort = await get_effort_data(context, user)
    live_box_drop_protocol = config.get_live_box_drop_protocol()
    current_amount = amount
    offer_limited_box_id = 0

    # TODO: Properly handle limited effort box
    while True:
        effort_spec = await get_effort_spec(context, current_effort.live_effort_point_box_spec_id)
        oldvalue = current_effort.current_point
        current_effort.current_point = min(oldvalue + current_amount, effort_spec.capacity)
        current_added = current_effort.current_point - oldvalue
        current_amount = current_amount - current_added

        if current_effort.current_point >= effort_spec.capacity:
            # Give reward
            drop_box_result = await live_box_drop_protocol.process_effort_box(
                context, current_effort.live_effort_point_box_spec_id, 0, amount
            )

            reward_list: list[EffortReward] = []
            for add_type, item_id, item_count, additional_data in drop_box_result.rewards:
                reward_data = EffortReward(add_type=add_type, item_id=item_id, amount=item_count)
                if additional_data:
                    for k, v in additional_data.items():
                        setattr(reward_data, k, v)

                await item.update_item_category_id(context, reward_data)
                reward_list.append(reward_data)

            result.append(
                EffortPointInfo(
                    live_effort_point_box_spec_id=current_effort.live_effort_point_box_spec_id,
                    capacity=effort_spec.capacity,
                    before=oldvalue,
                    after=current_effort.current_point,
                    rewards=reward_list,
                )
            )

            current_effort.live_effort_point_box_spec_id = drop_box_result.new_live_effort_point_box_spec_id
            current_effort.current_point = 0
            if drop_box_result.offer_limited_effort_event_id > 0:
                offer_limited_box_id = drop_box_result.offer_limited_effort_event_id

        if current_amount <= 0:
            break

    result.append(
        EffortPointInfo(
            live_effort_point_box_spec_id=current_effort.live_effort_point_box_spec_id,
            capacity=effort_spec.capacity,
            before=oldvalue,
            after=current_effort.current_point,
            rewards=[],
        )
    )
    return result, offer_limited_box_id
