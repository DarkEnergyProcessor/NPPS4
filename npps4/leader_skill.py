import math

from typing import Protocol


class _LeaderSkillCalcFunc(Protocol):
    def __call__(self, smile: int, pure: int, cool: int, by: float) -> tuple[int, int, int]: ...


def inc_smile(smile: int, pure: int, cool: int, by: float):
    return math.ceil(smile * by), 0, 0


def inc_pure(smile: int, pure: int, cool: int, by: float):
    return 0, math.ceil(pure * by), 0


def inc_cool(smile: int, pure: int, cool: int, by: float):
    return 0, 0, math.ceil(cool * by)


def inc_smile_by_pure(smile: int, pure: int, cool: int, by: float):
    return math.ceil(pure * by), 0, 0


def inc_smile_by_cool(smile: int, pure: int, cool: int, by: float):
    return math.ceil(cool * by), 0, 0


def inc_pure_by_smile(smile: int, pure: int, cool: int, by: float):
    return 0, math.ceil(smile * by), 0


def inc_pure_by_cool(smile: int, pure: int, cool: int, by: float):
    return 0, math.ceil(cool * by), 0


def inc_cool_by_smile(smile: int, pure: int, cool: int, by: float):
    return 0, 0, math.ceil(smile * by)


def inc_cool_by_pure(smile: int, pure: int, cool: int, by: float):
    return 0, 0, math.ceil(pure * by)


def _return_zero(smile: int, pure: int, cool: int, by: float):
    return 0, 0, 0


LEADER_SKILL_CALC_FUNC: dict[int, _LeaderSkillCalcFunc] = {
    1: inc_smile,
    2: inc_pure,
    3: inc_cool,
    112: inc_pure_by_smile,
    113: inc_cool_by_smile,
    121: inc_smile_by_pure,
    123: inc_cool_by_pure,
    131: inc_smile_by_cool,
    132: inc_pure_by_cool,
}


def calculate_bonus(leader_skill_effect_type: int, effect_value: int, smile: int, pure: int, cool: int):
    func = LEADER_SKILL_CALC_FUNC.get(leader_skill_effect_type, _return_zero)
    return func(smile, pure, cool, effect_value / 100)
