import functools

from typing import TYPE_CHECKING

##########################################################################################################
# Most of these information is obtained from https://w.atwiki.jp/lovelive-sif/pages/23.html unless noted #
##########################################################################################################


def _get_next_exp_base(rank: int) -> int:
    if rank <= 1:
        return 11
    elif rank < 34:
        # Rank < 34 is exactly this formula
        return round(_get_next_exp_base(rank - 1) + 34.45 * rank / 33)
    else:
        return round(34.45 * rank - 551)


def get_next_exp(rank: int):
    result: int = 0
    if rank > 0:
        result = _get_next_exp_base(rank)
        if rank < 100:
            result = round(result / 2)
    return result


def get_next_exp_cumulative(rank: int):
    return sum(map(get_next_exp, range(1, rank + 1)))


# functools.cache does not play very well with type checking right now.
if not TYPE_CHECKING:
    get_next_exp_cumulative = functools.cache(get_next_exp_cumulative)
    get_next_exp = functools.cache(get_next_exp)


def get_invite_code(user_id: int):
    # https://auahdark687291.blogspot.com/2018/05/sif-user-collision.html
    return (user_id * 805306357) % 999999937


def get_energy_by_rank(rank: int):
    lp1 = min(300, rank) // 2 + 25
    lp2 = max(rank - 300, 0) // 3
    return lp1 + lp2


def get_max_friend_by_rank(rank: int):
    friend1 = 10 + min(50, rank) // 5
    friend2 = max(rank - 50, 0) // 10
    return min(friend1 + friend2, 99)


def get_training_energy_by_rank(rank: int):
    m1 = 3 + min(200, rank) // 50
    m2 = max(rank - 200, 0) // 100
    return min(m1 + m2, 10)
