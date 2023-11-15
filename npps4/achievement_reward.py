from .const import ADD_TYPE
from .idol.system import item

_reward_def = item.add_loveca(1)
ACHIEVEMENT_REWARD_DEFAULT = item.Reward(
    add_type=_reward_def.add_type, item_id=_reward_def.item_id, amount=_reward_def.amount, reward_box_flag=True
)

# TODO: Get achievement present?
ACHIEVEMENT_REWARDS: dict[int, list[item.Reward]] = {
    103: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=4)],
    104: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=5)],
    105: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=6)],
}


def get(achievement_id: int):
    return ACHIEVEMENT_REWARDS.get(achievement_id, [ACHIEVEMENT_REWARD_DEFAULT])
