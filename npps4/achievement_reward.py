from .const import ADD_TYPE
from .idol.system import item

_reward_def = item.add_loveca(1)
ACHIEVEMENT_REWARD_DEFAULT = item.Reward(
    add_type=_reward_def.add_type, item_id=_reward_def.item_id, amount=_reward_def.amount, reward_box_flag=True
)

# TODO: Get achievement present?
ACHIEVEMENT_REWARDS: dict[int, list[item.Reward]] = {
    49: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    62: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=5)],
    103: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=4)],  # Reward: 1 - We are μ's (1st Years) - Story 1
    104: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=5)],  # Reward: 1 - We are μ's (1st Years) - Story 2
    106: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=6)],  # Reward: 1 - We are μ's (1st Years) - Story 3
    108: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=7)],  # 2 - We are μ's (3rd Years) - Story 1
    109: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=8)],  # 2 - We are μ's (3rd Years) - Story 2
    110: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=3)],  # Reward: Snow Halation
    111: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=9)],  # Reward: 2 - We are μ's (3rd Years) - Story 3
    113: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=10)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 1
    115: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=11)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 2
    116: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=5)],  # Reward: Natsuiro Egao de 1, 2, Jump!
    117: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=12)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 3
    119: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=13)],  # Reward: 4 - μ's Gets Interviewed?! - Story 1
    121: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=14)],  # Reward: 4 - μ's Gets Interviewed?! - Story 2
    122: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=7)],  # Reward: Mogyutto "Love" de Sekkinchu!
    123: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=15)],  # Reward: 4 - μ's Gets Interviewed?! - Story 3
    423: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=165)],
    483: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=202)],
    948: [item.Reward(add_type=ADD_TYPE.RECOVER_LP_ITEM, item_id=3, amount=10)],
    949: [item.Reward(add_type=ADD_TYPE.EXCHANGE_POINT, item_id=2, amount=20)],
    950: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=23, amount=9)],
    951: [item.Reward(add_type=ADD_TYPE.EXCHANGE_POINT, item_id=3, amount=10)],
    952: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=5, amount=25)],
    953: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=24, amount=9)],
    954: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=14101)],
    955: [item.Reward(add_type=ADD_TYPE.UNIT, item_id=2227)],
    956: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=93, amount=9)],
    957: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4, amount=50)],
    10010009: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    10040008: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    10090002: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=6)],
    10090003: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=7)],
    10090004: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=8)],
    10090005: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=9)],
    10090006: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=10)],
    10090007: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=11)],
    10090009: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=13)],
    10090011: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=15)],
    10090022: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=30)],
    10090023: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=31)],
    10090024: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=32)],
    10090025: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=33)],
    10090026: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=34)],
    10090027: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=35)],
    10090028: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=36)],
    10090029: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=37)],
    10090030: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=38)],
    10090031: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=39)],
    10090032: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=40)],
    10090033: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=41)],
    10090041: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=1)],
    10090162: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=269)],
    10093826: [item.Reward(add_type=ADD_TYPE.BACKGROUND, item_id=227)],
    10093843: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4, amount=3)],
    10093844: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4, amount=2)],
    10093850: [item.Reward(add_type=ADD_TYPE.BACKGROUND, item_id=228)],
    10100010: [item.Reward(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=40000)],
    10180011: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    10190014: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    10200007: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
    10260004: [item.Reward(add_type=ADD_TYPE.SOCIAL_POINT, item_id=2, amount=4000)],
    10290001: [item.Reward(add_type=ADD_TYPE.AWARD, item_id=2)],
    10290004: [
        item.Reward(add_type=ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=2),
        item.Reward(add_type=ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=1),
        item.Reward(add_type=ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=3),
    ],
    10290006: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=533)],
    10290009: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3006)],
    10290011: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3016)],
    10290014: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3007)],
    10290016: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3020)],
    10290019: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3008)],
    10290021: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3024)],
    10290024: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3009)],
    10290025: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3010)],
    10290026: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3011)],
    10290027: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3012)],
    10290028: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3013)],
    10290029: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3014)],
    10290030: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3029)],
    10290031: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3030)],
    10290032: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3031)],
    10290035: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3034)],
    10290036: [item.Reward(add_type=ADD_TYPE.UNIT_MAX, item_id=0, amount=100)],
    10290058: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3052)],
    10290059: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3051)],
    10290061: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3048)],
    10290062: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3057)],
    10290063: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3055)],
    10290064: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3053)],
    10290065: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3058)],
    10290066: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3054)],
    10290067: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3056)],
    10290068: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3050)],
    10290069: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3047)],
    10290074: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3061)],
    10290076: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3059)],
    10290078: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3060)],
    10290080: [item.Reward(add_type=ADD_TYPE.UNIT_MAX, item_id=0, amount=100)],
    10290088: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3062)],
    10290095: [
        item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3043),
        item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3044),
        item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3045),
    ],
    10290096: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=621)],
    10290097: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=632)],
    10290106: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=637)],
    10290107: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3078)],
    10290108: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3079)],
    10290109: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3080)],
    10290110: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3081)],
    10290111: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3082)],
    10290112: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3083)],
    10290113: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3084)],
    10290114: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3085)],
    10290115: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=641)],
    10290116: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=645)],
    10290117: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=649)],
    10290118: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=653)],
    10290119: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=659)],
    10290120: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=664)],
    10290121: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=672)],
    10290122: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=688)],
    10290123: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=698)],
    10290124: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=700)],
    10290127: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3088)],
    10290128: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3089)],
    10290132: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3092)],
    10290133: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3093)],
    10290136: [
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=631),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=636),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=640),
    ],
    10290137: [
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=650),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=651),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=652),
    ],
    10290138: [
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=658),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=661),
        item.Reward(add_type=ADD_TYPE.LIVE, item_id=656),
    ],
    10290139: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=663), item.Reward(add_type=ADD_TYPE.LIVE, item_id=687)],
    10290142: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=696)],
    10290143: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3098)],
    10290144: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3099)],
    10290147: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=691)],
    10290148: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=726)],
    10290149: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=728)],
    10290150: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=733)],
    10290151: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=739)],
    10290152: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=745)],
    10290153: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=750)],
    10290154: [item.Reward(add_type=ADD_TYPE.LIVE, item_id=757)],
    10290165: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3102)],
    10290166: [item.Reward(add_type=ADD_TYPE.SCENARIO, item_id=3103)],
    20010007: [
        item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4),
        item.Reward(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=10000),
        item.Reward(add_type=ADD_TYPE.SOCIAL_POINT, item_id=2, amount=200),
    ],
    20010015: [
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=89),
        item.Reward(add_type=ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010016: [
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=1024),
        item.Reward(add_type=ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010017: [
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=382),
        item.Reward(add_type=ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010018: [
        item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=632),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=1142),
    ],
    20010019: [
        item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=385),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=1354),
    ],
    20010020: [
        item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=384),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=1355),
    ],
    20010021: [
        item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=383),
        item.Reward(add_type=ADD_TYPE.UNIT, item_id=1356),
    ],
    50000001: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1597)],
    50000006: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1601)],
    50010001: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1)],
    50010002: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=2)],
    50010003: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=3)],
    50010004: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=4)],
    50010005: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=5)],
    50010006: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=6)],
    50010007: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=7)],
    50010008: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=8)],
    50010009: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=9)],
    50010190: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=190)],
    50020001: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=300)],
    50020002: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=301)],
    50020003: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=302)],
    50020004: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=303)],
    50020005: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=304)],
    50020006: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=305)],
    50020007: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=306)],
    50020008: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=307)],
    50020009: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=308)],
    50020010: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=309)],
    50020011: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=310)],
    50020012: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=311)],
    50020013: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=312)],
    50020014: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=313)],
    50020015: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=314)],
    50020016: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=315)],
    50020017: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=316)],
    50020018: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=317)],
    50020019: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=318)],
    50020020: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=319)],
    50020021: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=320)],
    50020022: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=321)],
    50020023: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=322)],
    50020024: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=323)],
    50020025: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=324)],
    50020026: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=325)],
    50020027: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=326)],
    50020028: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=327)],
    50020029: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=328)],
    50020030: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=329)],
    50020031: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=330)],
    50020032: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=331)],
    50020033: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=332)],
    50020034: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=333)],
    50020035: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=334)],
    50020036: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=335)],
    50020037: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=336)],
    50020038: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=337)],
    50020039: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=338)],
    50020040: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=339)],
    50020041: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=340)],
    50020042: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=341)],
    50020043: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=342)],
    50020044: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=343)],
    50020045: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=344)],
    50020046: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=345)],
    50020047: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=346)],
    50020048: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=347)],
    50020049: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=348)],
    50020050: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=349)],
    50020051: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=350)],
    50020052: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=351)],
    50030001: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=500)],
    50040037: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=636)],
    50040055: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=654)],
    50050001: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1857)],
    50050002: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1858)],
    50050003: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1859)],
    50050004: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1860)],
    50050007: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1863)],
    50050008: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1864)],
    50050009: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1865)],
    50050010: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1866)],
    50050011: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1867)],
    50050012: [item.Reward(add_type=ADD_TYPE.MUSEUM, item_id=1868)],
    100000001: [item.Reward(add_type=ADD_TYPE.GAME_COIN, item_id=3, amount=10000)],
    100000002: [item.Reward(add_type=ADD_TYPE.SOCIAL_POINT, item_id=2, amount=1000)],
    100000027: [item.Reward(add_type=ADD_TYPE.ITEM, item_id=5, amount=3)],
    200000001: [item.Reward(add_type=ADD_TYPE.LOVECA, item_id=4)],
}


def get(achievement_id: int):
    return ACHIEVEMENT_REWARDS.get(achievement_id, [ACHIEVEMENT_REWARD_DEFAULT])
