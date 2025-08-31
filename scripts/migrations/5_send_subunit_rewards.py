import npps4.script_dummy  # isort:skip

import sqlalchemy

import npps4.idol
import npps4.db.main
import npps4.system.achievement
import npps4.system.advanced
import npps4.system.user

revision = "5_send_subunit_rewards"
prev_revision = "4_update_achievement_reset_type"

FIXES_ACHIEVEMENT_IDS = [10090010, *range(10090012, 10090019)]


async def main(context: npps4.idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(npps4.db.main.Achievement).where(
        npps4.db.main.Achievement.achievement_id.in_(FIXES_ACHIEVEMENT_IDS),
        npps4.db.main.Achievement.is_accomplished == True,
        npps4.db.main.Achievement.is_reward_claimed == False,
    )

    async for ach in (await context.db.main.stream(q)).scalars():
        user = await npps4.system.user.get(context, ach.user_id)
        if user is None:
            continue

        rewards = await npps4.system.achievement.get_achievement_rewards(context, ach)
        for reward in rewards:
            await npps4.system.advanced.add_item(context, user, reward)
