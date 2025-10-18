import npps4.script_dummy  # isort:skip

import sqlalchemy

import npps4.idol
import npps4.db.main
import npps4.system.item
import npps4.system.live
import npps4.system.reward

revision = "7_give_loveca_to_cleared_songs"
prev_revision = "6_send_subunit_rewards_take2"

FIXES_ACHIEVEMENT_IDS = [10090010, *range(10090012, 10090019)]


async def main(context: npps4.idol.BasicSchoolIdolContext):
    q = sqlalchemy.select(npps4.db.main.User)

    async for target_user in await context.db.main.stream_scalars(q):
        live_difficulty_id_checked: set[int] = set()
        loveca = 0

        q = sqlalchemy.select(npps4.db.main.LiveClear).where(npps4.db.main.LiveClear.user_id == target_user.id)
        async for live_clear in await context.db.main.stream_scalars(q):
            if live_clear.live_difficulty_id in live_difficulty_id_checked:
                continue

            live_setting = await npps4.system.live.get_live_setting_from_difficulty_id(
                context, live_clear.live_difficulty_id
            )
            if live_setting is None:
                raise ValueError(f"invalid live_difficulty_id {live_clear.live_difficulty_id}")

            if live_setting.difficulty > 3:
                # User cleared Expert or higher. Give loveca directly.
                loveca = loveca + 1
            else:
                # User cleared Easy, Normal, or Hard. Only give loveca if all is cleared.
                enh_list = (
                    await npps4.system.live.get_enh_live_difficulty_ids(context, live_clear.live_difficulty_id)
                ).copy()
                enh_list[live_setting.difficulty] = live_clear.live_difficulty_id
                cleared = True

                for i in range(1, 4):
                    live_clear_data_adjacent = await npps4.system.live.get_live_clear_data(
                        context, target_user, enh_list[i]
                    )
                    if live_clear_data_adjacent is None or live_clear_data_adjacent.clear_cnt == 0:
                        cleared = False
                        break

                if cleared:
                    loveca = loveca + 1
                    live_difficulty_id_checked.update(enh_list.values())

        if loveca > 0:
            print(f"Given {loveca} loveca to user {target_user.id} ({target_user.invite_code})")
            item = npps4.system.item.loveca(loveca)
            await npps4.system.reward.add_item(context, target_user, item, "First Live Clear Bonuses")
