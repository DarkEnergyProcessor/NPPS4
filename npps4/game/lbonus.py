import pydantic

from .. import idol
from .. import util
from .. import strings
from ..idol.system import achievement
from ..idol.system import ad
from ..idol.system import advanced
from ..idol.system import class_system as class_system_module
from ..idol.system import effort
from ..idol.system import item
from ..idol.system import lbonus
from ..idol.system import museum
from ..idol.system import reward
from ..idol.system import user


class LoginBonusCalendarMonthInfo(pydantic.BaseModel):
    year: int
    month: int
    days: list[lbonus.LoginBonusCalendar]


class LoginBonusCalendarInfo(pydantic.BaseModel):
    current_date: str
    current_month: LoginBonusCalendarMonthInfo
    next_month: LoginBonusCalendarMonthInfo
    get_item: item.RewardWithCategory | None = None


class LoginBonusTotalLogin(pydantic.BaseModel):
    login_count: int
    remaining_count: int = 2147483647  # TODO
    reward: list[item.Reward] | None = None


class LoginBonusResponse(pydantic.BaseModel):
    sheets: list = pydantic.Field(default_factory=list)
    calendar_info: LoginBonusCalendarInfo
    ad_info: ad.AdInfo
    total_login_info: LoginBonusTotalLogin
    license_lbonus_list: list  # TODO
    class_system: class_system_module.ClassSystemData = pydantic.Field(
        default_factory=class_system_module.ClassSystemData
    )  # TODO
    start_dash_sheets: list  # TODO
    effort_point: list[effort.EffortResult]
    limited_effort_box: list  # TODO
    accomplished_achievement_list: list[achievement.AchievementData]
    unaccomplished_achievement_cnt: int
    after_user_info: user.UserInfoData
    added_achievement_list: list[achievement.AchievementData]
    new_achievement_cnt: int
    museum_info: museum.MuseumInfoData
    server_timestamp: int
    present_cnt: int


@idol.register("lbonus", "execute", batchable=False, xmc_verify=idol.XMCVerifyMode.CROSS, exclude_none=True)
async def lbonus_execute(context: idol.SchoolIdolUserParams) -> LoginBonusResponse:
    server_timestamp = util.time()
    current_datetime = util.datetime(server_timestamp)

    next_year, next_month_num = current_datetime.year, current_datetime.month + 1
    if next_month_num > 12:
        next_year = next_year + 1
        next_month_num = 1

    current_user = await user.get_current(context)
    current_month = await lbonus.get_calendar(context, current_datetime.year, current_datetime.month)
    next_month = await lbonus.get_calendar(context, next_year, next_month_num)
    login_count = await lbonus.get_login_count(context, current_user)
    lbonuses_day = await lbonus.days_login_bonus(context, current_user, current_datetime.year, current_datetime.month)
    present_count = await reward.count_presentbox(context, current_user)

    has_lbonus = current_datetime.day in lbonuses_day
    get_item = None
    add_effort_amount = 0
    achievement_list = achievement.AchievementContext()
    accomplished_rewards = []
    unaccomplished_rewards = []
    if not has_lbonus:
        reward_item = current_month[current_datetime.day - 1].item
        add_effort_amount = 100000
        login_count = login_count + 1
        present_count = present_count + 1
        reward_message = strings.format_simple(strings.get("lbonus", 12), current_datetime.month, current_datetime.day)
        # TODO: Add unit support
        await reward.add_item(context, current_user, reward_item, *reward_message)
        await lbonus.mark_login_bonus(
            context, current_user, current_datetime.year, current_datetime.month, current_datetime.day
        )
        get_item = item.RewardWithCategory(
            add_type=reward_item.add_type,
            item_id=reward_item.item_id,
            amount=reward_item.amount,
            reward_box_flag=False,
        )
        await item.update_item_category_id(context, get_item)
        lbonuses_day.add(current_datetime.day)
        # Do achievement check
        achievement_list.extend(
            await achievement.check_type_27(context, current_user, login_count)
            + await achievement.check_type_29(context, current_user)
        )
        accomplished_rewards.extend(
            [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.accomplished]
        )
        unaccomplished_rewards.extend(
            [await achievement.get_achievement_rewards(context, ach) for ach in achievement_list.new]
        )
        await advanced.fixup_achievement_reward(context, current_user, accomplished_rewards)
        await advanced.fixup_achievement_reward(context, current_user, unaccomplished_rewards)
        await advanced.process_achievement_reward(
            context, current_user, achievement_list.accomplished, accomplished_rewards
        )

    # Modify current_month
    for day in lbonuses_day:
        current_month[day - 1].received = True

    effort_result, effort_reward, _ = await effort.add_effort(context, current_user, add_effort_amount)
    if effort_reward:
        for rewards in effort_reward:
            for r in rewards:
                add_result = await advanced.add_item(context, current_user, r)
                if not add_result.success:
                    msg = strings.format_simple(
                        strings.get("lbonus", 12), current_datetime.month, current_datetime.day
                    )
                    await reward.add_item(context, current_user, r, *msg)

    current_date = f"{current_datetime.year}-{current_datetime.month}-{current_datetime.day}"

    return LoginBonusResponse(
        calendar_info=LoginBonusCalendarInfo(
            current_date=current_date,
            current_month=LoginBonusCalendarMonthInfo(
                year=current_datetime.year, month=current_datetime.month, days=current_month
            ),
            next_month=LoginBonusCalendarMonthInfo(year=next_year, month=next_month_num, days=next_month),
            get_item=get_item,
        ),
        ad_info=ad.AdInfo(),
        total_login_info=LoginBonusTotalLogin(login_count=login_count),
        license_lbonus_list=[],  # TODO
        start_dash_sheets=[],  # TODO
        effort_point=effort_result,
        limited_effort_box=[],  # TODO
        accomplished_achievement_list=await achievement.to_game_representation(
            context, achievement_list.accomplished, accomplished_rewards
        ),
        unaccomplished_achievement_cnt=await achievement.get_achievement_count(context, current_user, False),
        after_user_info=await user.get_user_info(context, current_user),
        added_achievement_list=await achievement.to_game_representation(
            context, achievement_list.new, unaccomplished_rewards
        ),
        new_achievement_cnt=len(achievement_list.new),
        museum_info=await museum.get_museum_info_data(context, current_user),
        server_timestamp=server_timestamp,
        present_cnt=present_count,
    )
