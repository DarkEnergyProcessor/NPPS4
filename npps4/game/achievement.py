import pydantic


from .. import idol
from .. import util
from ..idol.system import achievement
from ..idol.system import advanced
from ..idol.system import user


class AchievementUnaccomplishedFilter(pydantic.BaseModel):
    filter_category_id: int
    achievement_list: list[achievement.AchievementData]
    count: int
    is_last: bool = True


class AchievementUnaccomplishedResponse(pydantic.RootModel[list[AchievementUnaccomplishedFilter]]):
    pass


@idol.register("achievement", "unaccomplishList")
async def achievement_unaccomplishlist(context: idol.SchoolIdolUserParams) -> AchievementUnaccomplishedResponse:
    current_user = await user.get_current(context)
    filter_ids = await achievement.get_achievement_filter_ids(context)

    result: list[AchievementUnaccomplishedFilter] = []
    for fcat in filter_ids:
        unaccomplished = await achievement.get_unclaimed_achievements_by_filter_id(context, current_user, fcat)
        unaccomplished_rewards = [await achievement.get_achievement_rewards(context, ach) for ach in unaccomplished]
        ach_list = await achievement.to_game_representation(context, unaccomplished, unaccomplished_rewards)
        result.append(
            AchievementUnaccomplishedFilter(filter_category_id=fcat, achievement_list=ach_list, count=len(ach_list))
        )

    return AchievementUnaccomplishedResponse.model_validate(result)
