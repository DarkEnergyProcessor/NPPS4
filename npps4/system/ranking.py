import sqlalchemy

from .. import idol
from ..db import main

QUERY_PER_PAGE = 20


async def get_live_ranking(context: idol.BasicSchoolIdolContext, live_difficulty_id: int, page: int):
    q = (
        sqlalchemy.select(sqlalchemy.func.count())
        .select_from(main.LiveClear)
        .where(main.LiveClear.live_difficulty_id == live_difficulty_id, main.LiveClear.clear_cnt > 0)
    )
    result = await context.db.main.execute(q)
    total_cnt = result.scalar() or 0
    player_scores: list[tuple[int, int]] = []

    if total_cnt > 0:
        q = (
            sqlalchemy.select(main.LiveClear)
            .where(main.LiveClear.live_difficulty_id == live_difficulty_id, main.LiveClear.clear_cnt > 0)
            .order_by(main.LiveClear.hi_score.desc())
            .limit(QUERY_PER_PAGE)
            .offset(page * QUERY_PER_PAGE)
        )
        result = await context.db.main.execute(q)
        for row in result.scalars():
            player_scores.append((row.user_id, row.hi_score))

    return total_cnt, player_scores
