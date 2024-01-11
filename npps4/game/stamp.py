from .. import idol
from .. import util

import pydantic


class StampPosition(pydantic.BaseModel):
    position: int
    stamp_id: int


class StampSetting(pydantic.BaseModel):
    stamp_setting_id: int
    main_flag: int
    stamp_list: list[StampPosition]


class StampSettingInfo(pydantic.BaseModel):
    stamp_type: int
    setting_list: list[StampSetting]


class StampInfoResponse(pydantic.BaseModel):
    owning_stamp_ids: list[int]
    stamp_setting: list[StampSettingInfo]


STUB_DATA = {
    "owning_stamp_ids": [
        1001,
        1002,
        1003,
        1004,
        1005,
        1006,
        1007,
        1008,
        1009,
        1,
        2,
        19,
        3,
        4,
        20,
        5,
        6,
        21,
        7,
        8,
        22,
        9,
        10,
        23,
        11,
        12,
        24,
        13,
        14,
        25,
        15,
        16,
        26,
        17,
        18,
        27,
        201,
        101,
        102,
        119,
        103,
        104,
        120,
        105,
        106,
        121,
        107,
        108,
        122,
        109,
        110,
        123,
        111,
        112,
        124,
        113,
        114,
        125,
        115,
        116,
        126,
        117,
        118,
        127,
        301,
    ],
    "stamp_setting": [
        {
            "stamp_type": 1,
            "setting_list": [
                {
                    "stamp_setting_id": 1,
                    "main_flag": 1,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 2},
                        {"position": 2, "stamp_id": 101},
                        {"position": 3, "stamp_id": 4},
                        {"position": 4, "stamp_id": 103},
                        {"position": 5, "stamp_id": 5},
                        {"position": 6, "stamp_id": 105},
                        {"position": 7, "stamp_id": 7},
                        {"position": 8, "stamp_id": 108},
                        {"position": 9, "stamp_id": 10},
                        {"position": 10, "stamp_id": 110},
                        {"position": 11, "stamp_id": 12},
                        {"position": 12, "stamp_id": 112},
                        {"position": 13, "stamp_id": 13},
                        {"position": 14, "stamp_id": 114},
                        {"position": 15, "stamp_id": 16},
                        {"position": 16, "stamp_id": 116},
                        {"position": 17, "stamp_id": 17},
                        {"position": 18, "stamp_id": 117},
                    ],
                },
                {
                    "stamp_setting_id": 2,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 2},
                        {"position": 2, "stamp_id": 101},
                        {"position": 3, "stamp_id": 4},
                        {"position": 4, "stamp_id": 103},
                        {"position": 5, "stamp_id": 5},
                        {"position": 6, "stamp_id": 105},
                        {"position": 7, "stamp_id": 7},
                        {"position": 8, "stamp_id": 108},
                        {"position": 9, "stamp_id": 10},
                        {"position": 10, "stamp_id": 110},
                        {"position": 11, "stamp_id": 12},
                        {"position": 12, "stamp_id": 112},
                        {"position": 13, "stamp_id": 13},
                        {"position": 14, "stamp_id": 114},
                        {"position": 15, "stamp_id": 16},
                        {"position": 16, "stamp_id": 116},
                        {"position": 17, "stamp_id": 17},
                        {"position": 18, "stamp_id": 117},
                    ],
                },
                {
                    "stamp_setting_id": 3,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 2},
                        {"position": 2, "stamp_id": 101},
                        {"position": 3, "stamp_id": 4},
                        {"position": 4, "stamp_id": 103},
                        {"position": 5, "stamp_id": 5},
                        {"position": 6, "stamp_id": 105},
                        {"position": 7, "stamp_id": 7},
                        {"position": 8, "stamp_id": 108},
                        {"position": 9, "stamp_id": 10},
                        {"position": 10, "stamp_id": 110},
                        {"position": 11, "stamp_id": 12},
                        {"position": 12, "stamp_id": 112},
                        {"position": 13, "stamp_id": 13},
                        {"position": 14, "stamp_id": 114},
                        {"position": 15, "stamp_id": 16},
                        {"position": 16, "stamp_id": 116},
                        {"position": 17, "stamp_id": 17},
                        {"position": 18, "stamp_id": 117},
                    ],
                },
                {
                    "stamp_setting_id": 4,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 2},
                        {"position": 2, "stamp_id": 101},
                        {"position": 3, "stamp_id": 4},
                        {"position": 4, "stamp_id": 103},
                        {"position": 5, "stamp_id": 5},
                        {"position": 6, "stamp_id": 105},
                        {"position": 7, "stamp_id": 7},
                        {"position": 8, "stamp_id": 108},
                        {"position": 9, "stamp_id": 10},
                        {"position": 10, "stamp_id": 110},
                        {"position": 11, "stamp_id": 12},
                        {"position": 12, "stamp_id": 112},
                        {"position": 13, "stamp_id": 13},
                        {"position": 14, "stamp_id": 114},
                        {"position": 15, "stamp_id": 16},
                        {"position": 16, "stamp_id": 116},
                        {"position": 17, "stamp_id": 17},
                        {"position": 18, "stamp_id": 117},
                    ],
                },
                {
                    "stamp_setting_id": 5,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 2},
                        {"position": 2, "stamp_id": 101},
                        {"position": 3, "stamp_id": 4},
                        {"position": 4, "stamp_id": 103},
                        {"position": 5, "stamp_id": 5},
                        {"position": 6, "stamp_id": 105},
                        {"position": 7, "stamp_id": 7},
                        {"position": 8, "stamp_id": 108},
                        {"position": 9, "stamp_id": 10},
                        {"position": 10, "stamp_id": 110},
                        {"position": 11, "stamp_id": 12},
                        {"position": 12, "stamp_id": 112},
                        {"position": 13, "stamp_id": 13},
                        {"position": 14, "stamp_id": 114},
                        {"position": 15, "stamp_id": 16},
                        {"position": 16, "stamp_id": 116},
                        {"position": 17, "stamp_id": 17},
                        {"position": 18, "stamp_id": 117},
                    ],
                },
            ],
        },
        {
            "stamp_type": 2,
            "setting_list": [
                {
                    "stamp_setting_id": 1,
                    "main_flag": 1,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 1001},
                        {"position": 2, "stamp_id": 1002},
                        {"position": 3, "stamp_id": 1003},
                        {"position": 4, "stamp_id": 1004},
                        {"position": 5, "stamp_id": 1005},
                        {"position": 6, "stamp_id": 1006},
                        {"position": 7, "stamp_id": 1007},
                        {"position": 8, "stamp_id": 1008},
                        {"position": 9, "stamp_id": 1009},
                    ],
                },
                {
                    "stamp_setting_id": 2,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 1001},
                        {"position": 2, "stamp_id": 1002},
                        {"position": 3, "stamp_id": 1003},
                        {"position": 4, "stamp_id": 1004},
                        {"position": 5, "stamp_id": 1005},
                        {"position": 6, "stamp_id": 1006},
                        {"position": 7, "stamp_id": 1007},
                        {"position": 8, "stamp_id": 1008},
                        {"position": 9, "stamp_id": 1009},
                    ],
                },
                {
                    "stamp_setting_id": 3,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 1001},
                        {"position": 2, "stamp_id": 1002},
                        {"position": 3, "stamp_id": 1003},
                        {"position": 4, "stamp_id": 1004},
                        {"position": 5, "stamp_id": 1005},
                        {"position": 6, "stamp_id": 1006},
                        {"position": 7, "stamp_id": 1007},
                        {"position": 8, "stamp_id": 1008},
                        {"position": 9, "stamp_id": 1009},
                    ],
                },
                {
                    "stamp_setting_id": 4,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 1001},
                        {"position": 2, "stamp_id": 1002},
                        {"position": 3, "stamp_id": 1003},
                        {"position": 4, "stamp_id": 1004},
                        {"position": 5, "stamp_id": 1005},
                        {"position": 6, "stamp_id": 1006},
                        {"position": 7, "stamp_id": 1007},
                        {"position": 8, "stamp_id": 1008},
                        {"position": 9, "stamp_id": 1009},
                    ],
                },
                {
                    "stamp_setting_id": 5,
                    "main_flag": 0,
                    "stamp_list": [
                        {"position": 1, "stamp_id": 1001},
                        {"position": 2, "stamp_id": 1002},
                        {"position": 3, "stamp_id": 1003},
                        {"position": 4, "stamp_id": 1004},
                        {"position": 5, "stamp_id": 1005},
                        {"position": 6, "stamp_id": 1006},
                        {"position": 7, "stamp_id": 1007},
                        {"position": 8, "stamp_id": 1008},
                        {"position": 9, "stamp_id": 1009},
                    ],
                },
            ],
        },
    ],
}


@idol.register("stamp", "stampInfo")
async def stamp_stampinfo(context: idol.SchoolIdolUserParams) -> StampInfoResponse:
    # TODO
    util.stub("stamp", "stampInfo", context.raw_request_data)
    return StampInfoResponse.model_validate(STUB_DATA)
