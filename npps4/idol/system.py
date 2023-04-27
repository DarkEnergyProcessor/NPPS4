import functools


@functools.cache
def get_next_exp(rank: int):
    result: int = 0
    if rank > 0:
        if rank < 34:
            result = round(11 + (rank - 1) ** 1.8375)
        else:
            # https://w.atwiki.jp/lovelive-sif/pages/23.html
            result = round(34.45 * rank - 511)
        if rank < 100:
            result = round(result / 2)
    return result


@functools.cache
def get_next_exp_cumulative(rank: int):
    return sum(map(get_next_exp, range(1, rank + 1)))


def get_invite_code(user_id: int):
    # https://auahdark687291.blogspot.com/2018/05/sif-user-collision.html
    return (user_id * 805306357) % 999999937
