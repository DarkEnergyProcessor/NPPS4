import pydantic


from .. import idol
from .. import util
from ..idol.system import achievement
from ..idol.system import advanced
from ..idol.system import user


class AchievementUnaccomplishedFilter(pydantic.BaseModel):
    filter_category_id: int
    achievement_list: list[achievement.Achievement]
    count: int
    is_last: bool = True


@idol.register("achievement", "unaccomplishList")
async def achievement_unaccomplishlist(context: idol.SchoolIdolUserParams) -> list[AchievementUnaccomplishedFilter]:
    current_user = await user.get_current(context)
    unaccomplished = await achievement.get_achievements(context, current_user, False)
    await advanced.fixup_achievement_reward(context, current_user, unaccomplished)
    filter_ids = await achievement.get_achievement_filter_ids(context)

    result: list[AchievementUnaccomplishedFilter] = []
    for fcat in filter_ids:
        ach_list: list[achievement.Achievement] = []

        for ach in unaccomplished:
            ach_info = await achievement.get_achievement_info(context, ach.achievement_id)
            if ach_info is not None and ach_info.achievement_filter_category_id == fcat:
                ach_list.append(ach)

        result.append(
            AchievementUnaccomplishedFilter(filter_category_id=fcat, achievement_list=ach_list, count=len(ach_list))
        )

    return result
