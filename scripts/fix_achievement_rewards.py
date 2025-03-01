import npps4.script_dummy  # isort:skip

import collections.abc
import sqlalchemy

import npps4.const
import npps4.data
import npps4.idol
import npps4.db.main
import npps4.system.achievement
import npps4.system.award
import npps4.system.background
import npps4.system.item_model
import npps4.system.live
import npps4.system.museum
import npps4.system.scenario
import npps4.system.user

from typing import Any, Callable


def has_add_type(l: list[npps4.system.item_model.BaseItem], /, *add_types: npps4.const.ADD_TYPE):
    for v in l:
        if v.add_type in add_types:
            return True
    return False


class Fixer:
    def __init__(
        self,
        has: Callable[[npps4.idol.BasicSchoolIdolContext, npps4.db.main.User, int], collections.abc.Awaitable[bool]],
        add: Callable[
            [npps4.idol.BasicSchoolIdolContext, npps4.db.main.User, int], collections.abc.Awaitable[Any | None]
        ],
    ):
        self.has_call = has
        self.add_call = add

    async def has(
        self, context: npps4.idol.BasicSchoolIdolContext, target_user: npps4.db.main.User, identifier: int
    ) -> bool:
        return await self.has_call(context, target_user, identifier)

    async def add(
        self, context: npps4.idol.BasicSchoolIdolContext, target_user: npps4.db.main.User, identifier: int
    ) -> None:
        await self.add_call(context, target_user, identifier)


TO_FIX = {
    npps4.const.ADD_TYPE.LIVE: Fixer(npps4.system.live.has_normal_live_unlock, npps4.system.live.unlock_normal_live),
    npps4.const.ADD_TYPE.AWARD: Fixer(npps4.system.award.has_award, npps4.system.award.unlock_award),
    npps4.const.ADD_TYPE.BACKGROUND: Fixer(
        npps4.system.background.has_background, npps4.system.background.unlock_background
    ),
    npps4.const.ADD_TYPE.SCENARIO: Fixer(npps4.system.scenario.is_unlocked, npps4.system.scenario.unlock),
    npps4.const.ADD_TYPE.MUSEUM: Fixer(npps4.system.museum.has, npps4.system.museum.unlock),
}


async def run_script(args: list[str]):
    fixed_ach = set[int]()
    fixed_user = set[int]()

    achievement_reward = npps4.data.get().achievement_reward
    achievement_reward_target = {k: v for k, v in achievement_reward.items() if (has_add_type(v, *TO_FIX.keys()))}

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        q = sqlalchemy.select(npps4.db.main.Achievement).where(
            npps4.db.main.Achievement.achievement_id.in_(achievement_reward_target.keys()),
            npps4.db.main.Achievement.is_accomplished == True,
        )
        result = await context.db.main.execute(q)

        for ach_data in result.scalars():
            for reward_info in achievement_reward[ach_data.achievement_id]:
                if reward_info.add_type in TO_FIX:
                    fixer = TO_FIX[reward_info.add_type]
                    target = await npps4.system.user.get(context, ach_data.user_id)
                    assert target is not None
                    if not await fixer.has(context, target, reward_info.item_id):
                        await fixer.add(context, target, reward_info.item_id)
                        print(f"Fixed achievement_id {ach_data.achievement_id} for user_id {ach_data.user_id}")
                        fixed_ach.add(ach_data.id)
                        fixed_user.add(ach_data.user_id)

    print(f"Fixed {len(fixed_ach)} goal rewards across {len(fixed_user)} users")


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
