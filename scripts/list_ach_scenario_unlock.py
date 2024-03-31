#!/usr/bin/env python -m npps4.script
import sqlalchemy

import npps4.db.main
import npps4.db.achievement
import npps4.db.scenario
import npps4.idol


def select_en(jp: str, en: str | None):
    return en or jp


async def run_script(args: list[str]):
    context = npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en)

    async with context:
        # Get achievement that require main story unlocks
        q = sqlalchemy.select(npps4.db.achievement.Achievement).where(
            npps4.db.achievement.Achievement.achievement_type == 23
        )
        result = await context.db.achievement.execute(q)
        main_story_ach = dict((a.achievement_id, a) for a in result.scalars())

        fast_main_story_ach_lookup = set(main_story_ach.keys())
        q = sqlalchemy.select(npps4.db.achievement.Story).where(
            npps4.db.achievement.Story.next_achievement_id.in_(main_story_ach.keys())
        )
        result = await context.db.achievement.execute(q)
        ach_trees = list(filter(lambda a: a.next_achievement_id in fast_main_story_ach_lookup, result.scalars()))

        for ach_id in sorted(ach_trees, key=lambda k: k.achievement_id):
            ach = main_story_ach[ach_id.next_achievement_id]
            scenario_id = int(ach.params1 or 0)
            scenario = await context.db.scenario.get(npps4.db.scenario.Scenario, scenario_id)
            assert scenario is not None
            scenario_chapter = await context.db.scenario.get(npps4.db.scenario.Chapter, scenario.scenario_chapter_id)
            assert scenario_chapter is not None
            scenario_chapter_name = select_en(scenario_chapter.name, scenario_chapter.name_en)
            scenario_name = select_en(scenario.title, scenario.title_en)
            print(
                f"{ach_id.achievement_id}: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id={scenario_id})],  # Reward: {scenario_chapter_name} - {scenario_name}"
            )
