import pydantic

from . import item
from ... import idol
from ...db import main
from ...db import effort


class EffortReward(item.RewardWithCategory):
    rarity: int = 6  # TODO


class EffortResult(pydantic.BaseModel):
    live_effort_point_box_spec_id: int
    capacity: int
    before: int
    after: int
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
    result: list[EffortResult] = []
    rewards: list[EffortReward] = []
    current_effort = await get_effort_data(context, user)

    while True:
        effort_spec = await get_effort_spec(context, current_effort.live_effort_point_box_spec_id)
        oldvalue = current_effort.current_point
        current_effort.current_point = min(oldvalue + amount, effort_spec.capacity)
        amount = amount - (current_effort.current_point - oldvalue)

        if current_effort.current_point >= effort_spec.capacity:
            # Give present
            # FIXME: Proper drops. This is currently loveca + 1 at the moment.
            user.free_sns_coin = user.free_sns_coin + 1
            reward = EffortReward(add_type=3001, item_id=4, amount=1, reward_box_flag=False)
            rewards.append(reward)
            result.append(
                EffortResult(
                    live_effort_point_box_spec_id=current_effort.live_effort_point_box_spec_id,
                    capacity=effort_spec.capacity,
                    before=oldvalue,
                    after=current_effort.current_point,
                    rewards=[reward],
                )
            )
            # FIXME: Select effort point box spec
            current_effort.current_point = 0
        else:
            result.append(
                EffortResult(
                    live_effort_point_box_spec_id=current_effort.live_effort_point_box_spec_id,
                    capacity=effort_spec.capacity,
                    before=oldvalue,
                    after=current_effort.current_point,
                    rewards=[],
                )
            )
            break

    return result, rewards
