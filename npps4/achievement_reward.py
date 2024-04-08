from . import const
from .system import common
from .system import item
from .system import item_model
from .system import live_model
from .system import scenario_model

ACHIEVEMENT_REWARD_DEFAULT = item.loveca(1)

# TODO: Get achievement present?
ACHIEVEMENT_REWARDS: dict[int, list[common.AnyItem]] = {
    49: [item.loveca(1)],
    62: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=5)],
    103: [scenario_model.ScenarioItem(item_id=4)],  # Reward: 1 - We are μ's (1st Years) - Story 1
    104: [scenario_model.ScenarioItem(item_id=5)],  # Reward: 1 - We are μ's (1st Years) - Story 2
    106: [scenario_model.ScenarioItem(item_id=6)],  # Reward: 1 - We are μ's (1st Years) - Story 3
    108: [scenario_model.ScenarioItem(item_id=7)],  # Reward: 2 - We are μ's (3rd Years) - Story 1
    109: [scenario_model.ScenarioItem(item_id=8)],  # Reward: 2 - We are μ's (3rd Years) - Story 2
    110: [live_model.LiveItem(item_id=3)],  # Reward: Snow Halation
    111: [scenario_model.ScenarioItem(item_id=9)],  # Reward: 2 - We are μ's (3rd Years) - Story 3
    113: [scenario_model.ScenarioItem(item_id=10)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 1
    115: [scenario_model.ScenarioItem(item_id=11)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 2
    116: [live_model.LiveItem(item_id=5)],  # Reward: Natsuiro Egao de 1, 2, Jump!
    117: [scenario_model.ScenarioItem(item_id=12)],  # Reward: 3 - A Bigger Rehearsal Space! - Story 3
    119: [scenario_model.ScenarioItem(item_id=13)],  # Reward: 4 - μ's Gets Interviewed?! - Story 1
    121: [scenario_model.ScenarioItem(item_id=14)],  # Reward: 4 - μ's Gets Interviewed?! - Story 2
    122: [live_model.LiveItem(item_id=7)],  # Reward: Mogyutto "Love" de Sekkinchu!
    123: [scenario_model.ScenarioItem(item_id=15)],  # Reward: 4 - μ's Gets Interviewed?! - Story 3
    125: [scenario_model.ScenarioItem(item_id=16)],  # Reward: 5 - Student Council Helpers - Story 1
    127: [scenario_model.ScenarioItem(item_id=17)],  # Reward: 5 - Student Council Helpers - Story 2
    128: [live_model.LiveItem(item_id=9)],  # Reward: Wonderful Rush
    129: [scenario_model.ScenarioItem(item_id=18)],  # Reward: 5 - Student Council Helpers - Story 3
    131: [scenario_model.ScenarioItem(item_id=19)],  # Reward: 6 - Hanayo's Grand Diet Plan! - Story 1
    133: [scenario_model.ScenarioItem(item_id=20)],  # Reward: 6 - Hanayo's Grand Diet Plan! - Story 2
    134: [live_model.LiveItem(item_id=14)],  # Reward: WILD STARS
    135: [scenario_model.ScenarioItem(item_id=21)],  # Reward: 6 - Hanayo's Grand Diet Plan! - Story 3
    137: [scenario_model.ScenarioItem(item_id=22)],  # Reward: 7 - μ's Without Umi - Story 1
    139: [scenario_model.ScenarioItem(item_id=23)],  # Reward: 7 - μ's Without Umi - Story 2
    140: [live_model.LiveItem(item_id=21)],  # Reward: Kaguya no Shiro de Odoritai
    141: [scenario_model.ScenarioItem(item_id=24)],  # Reward: 7 - μ's Without Umi - Story 3
    143: [scenario_model.ScenarioItem(item_id=25)],  # Reward: 8 - Enter the Festival! - Story 1
    145: [scenario_model.ScenarioItem(item_id=26)],  # Reward: 8 - Enter the Festival! - Story 2
    146: [live_model.LiveItem(item_id=26)],  # Reward: No Brand Girls
    147: [scenario_model.ScenarioItem(item_id=27)],  # Reward: 8 - Enter the Festival! - Story 3
    149: [scenario_model.ScenarioItem(item_id=28)],  # Reward: 9 - We Can't Practice Today - Story 1
    150: [live_model.LiveItem(item_id=32)],  # Reward: Wonder Zone
    151: [scenario_model.ScenarioItem(item_id=29)],  # Reward: 9 - We Can't Practice Today - Story 2
    153: [scenario_model.ScenarioItem(item_id=30)],  # Reward: 9 - We Can't Practice Today - Story 3
    154: [live_model.LiveItem(item_id=23)],  # Reward: Love Novels
    155: [scenario_model.ScenarioItem(item_id=31)],  # Reward: 9 - We Can't Practice Today - Story 4
    157: [scenario_model.ScenarioItem(item_id=32)],  # Reward: 10 - Summer Festival Fortunes - Story 1
    158: [live_model.LiveItem(item_id=40)],  # Reward: Korekara no Someday
    159: [scenario_model.ScenarioItem(item_id=33)],  # Reward: 10 - Summer Festival Fortunes - Story 2
    161: [scenario_model.ScenarioItem(item_id=34)],  # Reward: 10 - Summer Festival Fortunes - Story 3
    162: [live_model.LiveItem(item_id=15)],  # Reward: Shiranai Love * Oshiete Love
    163: [scenario_model.ScenarioItem(item_id=35)],  # Reward: 10 - Summer Festival Fortunes - Story 4
    165: [scenario_model.ScenarioItem(item_id=36)],  # Reward: 11 - The Tastiest Season - Story 1
    166: [live_model.LiveItem(item_id=55)],  # Reward: START: DASH!!
    167: [scenario_model.ScenarioItem(item_id=37)],  # Reward: 11 - The Tastiest Season - Story 2
    169: [scenario_model.ScenarioItem(item_id=38)],  # Reward: 11 - The Tastiest Season - Story 3
    170: [live_model.LiveItem(item_id=12)],  # Reward: Sweet & Sweet Holiday
    171: [scenario_model.ScenarioItem(item_id=39)],  # Reward: 11 - The Tastiest Season - Story 4
    173: [scenario_model.ScenarioItem(item_id=40)],  # Reward: 12 - The Festival Begins! - Story 1
    174: [live_model.LiveItem(item_id=79)],  # Reward: Ai wa Taiyo jyanai?
    175: [scenario_model.ScenarioItem(item_id=41)],  # Reward: 12 - The Festival Begins! - Story 2
    177: [scenario_model.ScenarioItem(item_id=42)],  # Reward: 12 - The Festival Begins! - Story 3
    178: [live_model.LiveItem(item_id=35)],  # Reward: Diamond Princess no Yuutsu
    179: [scenario_model.ScenarioItem(item_id=43)],  # Reward: 12 - The Festival Begins! - Story 4
    181: [scenario_model.ScenarioItem(item_id=44)],  # Reward: 13 - School Idol Festival - Story 1
    182: [live_model.LiveItem(item_id=11)],  # Reward: Love Marginal
    183: [scenario_model.ScenarioItem(item_id=45)],  # Reward: 13 - School Idol Festival - Story 2
    185: [scenario_model.ScenarioItem(item_id=46)],  # Reward: 13 - School Idol Festival - Story 3
    186: [live_model.LiveItem(item_id=141)],  # Reward: Takaramonos
    187: [scenario_model.ScenarioItem(item_id=47)],  # Reward: 13 - School Idol Festival - Story 4
    189: [scenario_model.ScenarioItem(item_id=48)],  # Reward: 14 - We Love Sweets! - Story 1
    190: [live_model.LiveItem(item_id=146)],  # Reward: Paradise Live
    191: [scenario_model.ScenarioItem(item_id=49)],  # Reward: 14 - We Love Sweets! - Story 2
    193: [scenario_model.ScenarioItem(item_id=50)],  # Reward: 14 - We Love Sweets! - Story 3
    194: [live_model.LiveItem(item_id=39)],  # Reward: Listen to My Heart!
    195: [scenario_model.ScenarioItem(item_id=51)],  # Reward: 14 - We Love Sweets! - Story 4
    197: [scenario_model.ScenarioItem(item_id=52)],  # Reward: 15 - Winter Wonderland - Story 1
    198: [live_model.LiveItem(item_id=166)],  # Reward: Music S.T.A.R.T!!
    199: [scenario_model.ScenarioItem(item_id=53)],  # Reward: 15 - Winter Wonderland - Story 2
    201: [scenario_model.ScenarioItem(item_id=54)],  # Reward: 15 - Winter Wonderland - Story 3
    202: [live_model.LiveItem(item_id=45)],  # Reward: Anone Ganbare!
    203: [scenario_model.ScenarioItem(item_id=55)],  # Reward: 15 - Winter Wonderland - Story 4
    205: [scenario_model.ScenarioItem(item_id=56)],  # Reward: 16 - Mountain Hike/Scary Test - Story 1
    206: [live_model.LiveItem(item_id=186)],  # Reward: LOVELESS WORLD
    207: [scenario_model.ScenarioItem(item_id=57)],  # Reward: 16 - Mountain Hike/Scary Test - Story 2
    209: [scenario_model.ScenarioItem(item_id=58)],  # Reward: 16 - Mountain Hike/Scary Test - Story 3
    210: [live_model.LiveItem(item_id=51)],  # Reward: After School NAVIGATORS
    211: [scenario_model.ScenarioItem(item_id=59)],  # Reward: 16 - Mountain Hike/Scary Test - Story 4
    213: [scenario_model.ScenarioItem(item_id=60)],  # Reward: 17 - This Is Our Home - Story 1
    214: [live_model.LiveItem(item_id=197)],  # Reward: LONELIEST BABY
    215: [scenario_model.ScenarioItem(item_id=61)],  # Reward: 17 - This Is Our Home - Story 2
    217: [scenario_model.ScenarioItem(item_id=62)],  # Reward: 17 - This Is Our Home - Story 3
    218: [live_model.LiveItem(item_id=67)],  # Reward: Cutie Panther
    219: [scenario_model.ScenarioItem(item_id=63)],  # Reward: 17 - This Is Our Home - Story 4
    221: [scenario_model.ScenarioItem(item_id=64)],  # Reward: 18 - Alpaca Escape!/Nine Paths - Story 1
    222: [live_model.LiveItem(item_id=214)],  # Reward: It's our miraculous time
    223: [scenario_model.ScenarioItem(item_id=65)],  # Reward: 18 - Alpaca Escape!/Nine Paths - Story 2
    225: [scenario_model.ScenarioItem(item_id=66)],  # Reward: 18 - Alpaca Escape!/Nine Paths - Story 3
    226: [live_model.LiveItem(item_id=123)],  # Reward: Pure Girls Project
    227: [scenario_model.ScenarioItem(item_id=67)],  # Reward: 18 - Alpaca Escape!/Nine Paths - Story 4
    229: [scenario_model.ScenarioItem(item_id=68)],  # Reward: 19 - Rain, Rain, Go Away - Story 1
    230: [live_model.LiveItem(item_id=230)],  # Reward: Donna Tokimo Zutto
    231: [scenario_model.ScenarioItem(item_id=69)],  # Reward: 19 - Rain, Rain, Go Away - Story 2
    233: [scenario_model.ScenarioItem(item_id=70)],  # Reward: 19 - Rain, Rain, Go Away - Story 3
    234: [live_model.LiveItem(item_id=163)],  # Reward: Binetsu kara Mystery
    235: [scenario_model.ScenarioItem(item_id=71)],  # Reward: 19 - Rain, Rain, Go Away - Story 4
    237: [scenario_model.ScenarioItem(item_id=72)],  # Reward: 20 - Star Festival Fireworks - Story 1
    238: [live_model.LiveItem(item_id=242)],  # Reward: Yume no Tobira
    239: [scenario_model.ScenarioItem(item_id=73)],  # Reward: 20 - Star Festival Fireworks - Story 2
    241: [scenario_model.ScenarioItem(item_id=74)],  # Reward: 20 - Star Festival Fireworks - Story 3
    242: [live_model.LiveItem(item_id=182)],  # Reward: Natsu Owaranaide.
    243: [scenario_model.ScenarioItem(item_id=75)],  # Reward: 20 - Star Festival Fireworks - Story 4
    245: [scenario_model.ScenarioItem(item_id=76)],  # Reward: 21 - Fun at the Pool! - Story 1
    246: [live_model.LiveItem(item_id=256)],  # Reward: Love Wing Bell
    247: [scenario_model.ScenarioItem(item_id=77)],  # Reward: 21 - Fun at the Pool! - Story 2
    249: [scenario_model.ScenarioItem(item_id=78)],  # Reward: 21 - Fun at the Pool! - Story 3
    250: [live_model.LiveItem(item_id=193)],  # Reward: UNBALANCED LOVE
    251: [scenario_model.ScenarioItem(item_id=79)],  # Reward: 21 - Fun at the Pool! - Story 4
    253: [scenario_model.ScenarioItem(item_id=80)],  # Reward: 22 - Otonokizaka's Open Campus - Story 1
    254: [live_model.LiveItem(item_id=272)],  # Reward: Dancing Stars on Me!
    255: [scenario_model.ScenarioItem(item_id=81)],  # Reward: 22 - Otonokizaka's Open Campus - Story 2
    257: [scenario_model.ScenarioItem(item_id=82)],  # Reward: 22 - Otonokizaka's Open Campus - Story 3
    258: [live_model.LiveItem(item_id=143)],  # Reward: Kimi no kuse ni!
    259: [scenario_model.ScenarioItem(item_id=83)],  # Reward: 22 - Otonokizaka's Open Campus - Story 4
    261: [scenario_model.ScenarioItem(item_id=84)],  # Reward: 23 - Shrine Helpers - Story 1
    262: [live_model.LiveItem(item_id=286)],  # Reward: KiRa-KiRa Sensation!
    263: [scenario_model.ScenarioItem(item_id=85)],  # Reward: 23 - Shrine Helpers - Story 2
    265: [scenario_model.ScenarioItem(item_id=86)],  # Reward: 23 - Shrine Helpers - Story 3
    266: [live_model.LiveItem(item_id=238)],  # Reward: Arifureta Kanashimi no Hate
    267: [scenario_model.ScenarioItem(item_id=87)],  # Reward: 23 - Shrine Helpers - Story 4
    269: [scenario_model.ScenarioItem(item_id=88)],  # Reward: 24 - Let's Cheer for Umi! - Story 1
    270: [live_model.LiveItem(item_id=299)],  # Reward: Happy Maker!
    271: [scenario_model.ScenarioItem(item_id=89)],  # Reward: 24 - Let's Cheer for Umi! - Story 2
    273: [scenario_model.ScenarioItem(item_id=90)],  # Reward: 24 - Let's Cheer for Umi! - Story 3
    274: [live_model.LiveItem(item_id=207)],  # Reward: Kodoku na Heaven
    275: [scenario_model.ScenarioItem(item_id=91)],  # Reward: 24 - Let's Cheer for Umi! - Story 4
    277: [scenario_model.ScenarioItem(item_id=92)],  # Reward: 25 - Merry Christmas - Story 1
    278: [live_model.LiveItem(item_id=313)],  # Reward: Datte Datte Aa Mujo
    279: [scenario_model.ScenarioItem(item_id=93)],  # Reward: 25 - Merry Christmas - Story 2
    281: [scenario_model.ScenarioItem(item_id=94)],  # Reward: 25 - Merry Christmas - Story 3
    282: [live_model.LiveItem(item_id=226)],  # Reward: Someday of My Life
    283: [scenario_model.ScenarioItem(item_id=95)],  # Reward: 25 - Merry Christmas - Story 4
    285: [scenario_model.ScenarioItem(item_id=96)],  # Reward: 26 - Trio Trials! - Story 1
    286: [live_model.LiveItem(item_id=327)],  # Reward: COLORFUL VOICE
    287: [scenario_model.ScenarioItem(item_id=97)],  # Reward: 26 - Trio Trials! - Story 2
    289: [scenario_model.ScenarioItem(item_id=98)],  # Reward: 26 - Trio Trials! - Story 3
    290: [live_model.LiveItem(item_id=251)],  # Reward: Blueberry ♡ Train
    291: [scenario_model.ScenarioItem(item_id=99)],  # Reward: 26 - Trio Trials! - Story 4
    293: [scenario_model.ScenarioItem(item_id=100)],  # Reward: 27 - Chocolates are Trouble! - Story 1
    294: [live_model.LiveItem(item_id=334)],  # Reward: SENTIMENTAL StepS
    295: [scenario_model.ScenarioItem(item_id=101)],  # Reward: 27 - Chocolates are Trouble! - Story 2
    297: [scenario_model.ScenarioItem(item_id=102)],  # Reward: 27 - Chocolates are Trouble! - Story 3
    298: [live_model.LiveItem(item_id=268)],  # Reward: Daring!!
    299: [scenario_model.ScenarioItem(item_id=103)],  # Reward: 27 - Chocolates are Trouble! - Story 4
    301: [scenario_model.ScenarioItem(item_id=104)],  # Reward: 28 - Yazawa Girls' Festival - Story 1
    302: [live_model.LiveItem(item_id=365)],  # Reward: Mo Hitori jyanaiyo
    303: [scenario_model.ScenarioItem(item_id=105)],  # Reward: 28 - Yazawa Girls' Festival - Story 2
    305: [scenario_model.ScenarioItem(item_id=106)],  # Reward: 28 - Yazawa Girls' Festival - Story 3
    306: [live_model.LiveItem(item_id=281)],  # Reward: Yuki no Reason
    307: [scenario_model.ScenarioItem(item_id=107)],  # Reward: 28 - Yazawa Girls' Festival - Story 4
    309: [scenario_model.ScenarioItem(item_id=108)],  # Reward: 29 - Songwriting Retreat - Story 1
    310: [live_model.LiveItem(item_id=374)],  # Reward: Watashitachi wa Mirai no Hana
    311: [scenario_model.ScenarioItem(item_id=109)],  # Reward: 29 - Songwriting Retreat - Story 2
    313: [scenario_model.ScenarioItem(item_id=110)],  # Reward: 29 - Songwriting Retreat - Story 3
    314: [live_model.LiveItem(item_id=294)],  # Reward: Koi no Signal Rin Rin Rin!
    315: [scenario_model.ScenarioItem(item_id=111)],  # Reward: 29 - Songwriting Retreat - Story 4
    317: [scenario_model.ScenarioItem(item_id=112)],  # Reward: 30 - Worried About Maki?! - Story 1
    318: [live_model.LiveItem(item_id=395)],  # Reward: Spicaterrible
    319: [scenario_model.ScenarioItem(item_id=113)],  # Reward: 30 - Worried About Maki?! - Story 2
    321: [scenario_model.ScenarioItem(item_id=114)],  # Reward: 30 - Worried About Maki?! - Story 3
    322: [live_model.LiveItem(item_id=322)],  # Reward: Mahotsukai Hajimemashita!
    323: [scenario_model.ScenarioItem(item_id=115)],  # Reward: 30 - Worried About Maki?! - Story 4
    325: [scenario_model.ScenarioItem(item_id=116)],  # Reward: 31 - Unsung Heroes - Story 1
    326: [live_model.LiveItem(item_id=309)],  # Reward: Junai Lens
    327: [scenario_model.ScenarioItem(item_id=117)],  # Reward: 31 - Unsung Heroes - Story 2
    329: [scenario_model.ScenarioItem(item_id=118)],  # Reward: 31 - Unsung Heroes - Story 3
    330: [live_model.LiveItem(item_id=419)],  # Reward: Angelic Angel
    331: [scenario_model.ScenarioItem(item_id=119)],  # Reward: 31 - Unsung Heroes - Story 4
    333: [scenario_model.ScenarioItem(item_id=120)],  # Reward: 32 - μ's Versus A-RISE - Story 1
    334: [live_model.LiveItem(item_id=427)],  # Reward: Private Wars
    335: [scenario_model.ScenarioItem(item_id=121)],  # Reward: 32 - μ's Versus A-RISE - Story 2
    337: [scenario_model.ScenarioItem(item_id=122)],  # Reward: 32 - μ's Versus A-RISE - Story 3
    338: [live_model.LiveItem(item_id=369)],  # Reward: Futari Happiness
    339: [scenario_model.ScenarioItem(item_id=123)],  # Reward: 32 - μ's Versus A-RISE - Story 4
    341: [scenario_model.ScenarioItem(item_id=124)],  # Reward: 33 - The Sister Swap - Story 1
    342: [live_model.LiveItem(item_id=442)],  # Reward: SUNNY DAY SONG
    343: [scenario_model.ScenarioItem(item_id=125)],  # Reward: 33 - The Sister Swap - Story 2
    345: [scenario_model.ScenarioItem(item_id=126)],  # Reward: 33 - The Sister Swap - Story 3
    346: [live_model.LiveItem(item_id=396)],  # Reward: Trouble Busters
    347: [scenario_model.ScenarioItem(item_id=127)],  # Reward: 33 - The Sister Swap - Story 4
    349: [scenario_model.ScenarioItem(item_id=128)],  # Reward: 34 - Homura Bakery! - Story 1
    350: [live_model.LiveItem(item_id=444)],  # Reward: Bokutachi wa Hitotsu no Hikari
    351: [scenario_model.ScenarioItem(item_id=129)],  # Reward: 34 - Homura Bakery! - Story 2
    353: [scenario_model.ScenarioItem(item_id=130)],  # Reward: 34 - Homura Bakery! - Story 3
    354: [live_model.LiveItem(item_id=336)],  # Reward: Nightingale Love Song
    355: [scenario_model.ScenarioItem(item_id=131)],  # Reward: 34 - Homura Bakery! - Story 4
    357: [scenario_model.ScenarioItem(item_id=132)],  # Reward: 35 - Honoka's Love Song - Story 1
    358: [live_model.LiveItem(item_id=421)],  # Reward: Shiawase yuki no SMILING!
    359: [scenario_model.ScenarioItem(item_id=133)],  # Reward: 35 - Honoka's Love Song - Story 2
    361: [scenario_model.ScenarioItem(item_id=134)],  # Reward: 35 - Honoka's Love Song - Story 3
    362: [live_model.LiveItem(item_id=447)],  # Reward: HEART to HEART!
    363: [scenario_model.ScenarioItem(item_id=135)],  # Reward: 35 - Honoka's Love Song - Story 4
    365: [scenario_model.ScenarioItem(item_id=136)],  # Reward: 36 - Hanayo's Disciple! - Story 1
    366: [live_model.LiveItem(item_id=448)],  # Reward: Arashi no Naka no Koi dakara
    367: [scenario_model.ScenarioItem(item_id=137)],  # Reward: 36 - Hanayo's Disciple! - Story 2
    369: [scenario_model.ScenarioItem(item_id=138)],  # Reward: 36 - Hanayo's Disciple! - Story 3
    370: [live_model.LiveItem(item_id=443)],  # Reward: Moshimo Kara Kitto
    371: [scenario_model.ScenarioItem(item_id=139)],  # Reward: 36 - Hanayo's Disciple! - Story 4
    373: [scenario_model.ScenarioItem(item_id=140)],  # Reward: 37 - Big Cleanup! - Story 1
    374: [live_model.LiveItem(item_id=451)],  # Reward: Shocking Party
    375: [scenario_model.ScenarioItem(item_id=141)],  # Reward: 37 - Big Cleanup! - Story 2
    377: [scenario_model.ScenarioItem(item_id=142)],  # Reward: 37 - Big Cleanup! - Story 3
    378: [live_model.LiveItem(item_id=445)],  # Reward: Suki desu ga Suki desu ka?
    379: [scenario_model.ScenarioItem(item_id=143)],  # Reward: 37 - Big Cleanup! - Story 4
    381: [scenario_model.ScenarioItem(item_id=144)],  # Reward: 38 - School Idol Trip 1 - Story 1
    382: [live_model.LiveItem(item_id=455)],  # Reward: Mi wa μ'sic no Mi
    383: [scenario_model.ScenarioItem(item_id=145)],  # Reward: 38 - School Idol Trip 1 - Story 2
    385: [scenario_model.ScenarioItem(item_id=146)],  # Reward: 38 - School Idol Trip 1 - Story 3
    386: [live_model.LiveItem(item_id=449)],  # Reward: Zurui yo Magnetic Today
    387: [scenario_model.ScenarioItem(item_id=147)],  # Reward: 38 - School Idol Trip 1 - Story 4
    389: [scenario_model.ScenarioItem(item_id=148)],  # Reward: 39 - School Idol Trip 2 - Story 1
    390: [live_model.LiveItem(item_id=458)],  # Reward: Super LOVE = Super LIVE!
    391: [scenario_model.ScenarioItem(item_id=149)],  # Reward: 39 - School Idol Trip 2 - Story 2
    393: [scenario_model.ScenarioItem(item_id=150)],  # Reward: 39 - School Idol Trip 2 - Story 3
    394: [live_model.LiveItem(item_id=454)],  # Reward: Kururin MIRACLE
    395: [scenario_model.ScenarioItem(item_id=151)],  # Reward: 39 - School Idol Trip 2 - Story 4
    397: [scenario_model.ScenarioItem(item_id=152)],  # Reward: 40 - Chouchou the Cat - Story 1
    398: [live_model.LiveItem(item_id=460)],  # Reward: MOMENT RING
    399: [scenario_model.ScenarioItem(item_id=153)],  # Reward: 40 - Chouchou the Cat - Story 2
    401: [scenario_model.ScenarioItem(item_id=154)],  # Reward: 40 - Chouchou the Cat - Story 3
    402: [live_model.LiveItem(item_id=459)],  # Reward: Storm in Lover
    403: [scenario_model.ScenarioItem(item_id=155)],  # Reward: 40 - Chouchou the Cat - Story 4
    405: [scenario_model.ScenarioItem(item_id=156)],  # Reward: 41 - Mother's Day - Story 1
    406: [live_model.LiveItem(item_id=461)],  # Reward: Sayounara e Sayounara!
    407: [scenario_model.ScenarioItem(item_id=157)],  # Reward: 41 - Mother's Day - Story 2
    409: [scenario_model.ScenarioItem(item_id=158)],  # Reward: 41 - Mother's Day - Story 3
    410: [live_model.LiveItem(item_id=464)],  # Reward: NO EXIT ORION
    411: [scenario_model.ScenarioItem(item_id=159)],  # Reward: 41 - Mother's Day - Story 4
    413: [scenario_model.ScenarioItem(item_id=160)],  # Reward: 42 - Field Day Fury! - Story 1
    414: [live_model.LiveItem(item_id=465)],  # Reward: Shangri-La Shower
    415: [scenario_model.ScenarioItem(item_id=161)],  # Reward: 42 - Field Day Fury! - Story 2
    417: [scenario_model.ScenarioItem(item_id=162)],  # Reward: 42 - Field Day Fury! - Story 3
    418: [live_model.LiveItem(item_id=466)],  # Reward: Shunjo Romantic
    419: [scenario_model.ScenarioItem(item_id=163)],  # Reward: 42 - Field Day Fury! - Story 4
    421: [scenario_model.ScenarioItem(item_id=164)],  # Reward: 43 - Shopping on a Rainy Day - Story 1
    422: [live_model.LiveItem(item_id=469)],  # Reward: Ruteshi Kisuki Shiteru
    423: [scenario_model.ScenarioItem(item_id=165)],  # Reward: 43 - Shopping on a Rainy Day - Story 2
    425: [scenario_model.ScenarioItem(item_id=166)],  # Reward: 43 - Shopping on a Rainy Day - Story 3
    426: [live_model.LiveItem(item_id=472)],  # Reward: PSYCHIC FIRE
    427: [scenario_model.ScenarioItem(item_id=167)],  # Reward: 43 - Shopping on a Rainy Day - Story 4
    429: [scenario_model.ScenarioItem(item_id=168)],  # Reward: 44 - A Luxurious Trip - Story 1
    430: [live_model.LiveItem(item_id=475)],  # Reward: Soshite Saigo no Page ni wa
    431: [scenario_model.ScenarioItem(item_id=169)],  # Reward: 44 - A Luxurious Trip - Story 2
    433: [scenario_model.ScenarioItem(item_id=189)],  # Reward: 1 - We are Aqours! - Story 1
    435: [scenario_model.ScenarioItem(item_id=190)],  # Reward: 1 - We are Aqours! - Story 2
    437: [scenario_model.ScenarioItem(item_id=170)],  # Reward: 44 - A Luxurious Trip - Story 3
    438: [live_model.LiveItem(item_id=462)],  # Reward: Puwa Puwa-O!
    439: [scenario_model.ScenarioItem(item_id=171)],  # Reward: 44 - A Luxurious Trip - Story 4
    441: [scenario_model.ScenarioItem(item_id=191)],  # Reward: 1 - We are Aqours! - Story 3
    442: [live_model.LiveItem(item_id=477)],  # Reward: Aozora Jumping Heart
    443: [scenario_model.ScenarioItem(item_id=192)],  # Reward: 1 - We are Aqours! - Story 4
    445: [scenario_model.ScenarioItem(item_id=172)],  # Reward: 45 - Let's Go Farming! - Story 1
    447: [scenario_model.ScenarioItem(item_id=173)],  # Reward: 45 - Let's Go Farming! - Story 2
    449: [scenario_model.ScenarioItem(item_id=193)],  # Reward: 2 - What's a School Idol? - Story 1
    450: [live_model.LiveItem(item_id=479)],  # Reward: Yume Kataruyori Yume Utaou
    451: [scenario_model.ScenarioItem(item_id=194)],  # Reward: 2 - What's a School Idol? - Story 2
    453: [scenario_model.ScenarioItem(item_id=174)],  # Reward: 45 - Let's Go Farming! - Story 3
    454: [live_model.LiveItem(item_id=482)],  # Reward: Hello, Hoshiwo Kazoete
    455: [scenario_model.ScenarioItem(item_id=175)],  # Reward: 45 - Let's Go Farming! - Story 4
    457: [scenario_model.ScenarioItem(item_id=195)],  # Reward: 2 - What's a School Idol? - Story 3
    459: [scenario_model.ScenarioItem(item_id=196)],  # Reward: 2 - What's a School Idol? - Story 4
    461: [scenario_model.ScenarioItem(item_id=176)],  # Reward: 46 - Nozomi's Secret - Story 1
    463: [scenario_model.ScenarioItem(item_id=177)],  # Reward: 46 - Nozomi's Secret - Story 2
    465: [scenario_model.ScenarioItem(item_id=197)],  # Reward: 3 - Sparkle by the Pool! - Story 1
    466: [live_model.LiveItem(item_id=476)],  # Reward: Kimetayo Hand in Hand
    467: [scenario_model.ScenarioItem(item_id=198)],  # Reward: 3 - Sparkle by the Pool! - Story 2
    469: [scenario_model.ScenarioItem(item_id=178)],  # Reward: 46 - Nozomi's Secret - Story 3
    470: [live_model.LiveItem(item_id=484)],  # Reward: ?←HEARTBEAT
    471: [scenario_model.ScenarioItem(item_id=179)],  # Reward: 46 - Nozomi's Secret - Story 4
    473: [scenario_model.ScenarioItem(item_id=199)],  # Reward: 3 - Sparkle by the Pool! - Story 3
    475: [scenario_model.ScenarioItem(item_id=200)],  # Reward: 3 - Sparkle by the Pool! - Story 4
    477: [scenario_model.ScenarioItem(item_id=180)],  # Reward: 47 - The Miracle Nine - Story 1
    479: [scenario_model.ScenarioItem(item_id=181)],  # Reward: 47 - The Miracle Nine - Story 2
    481: [scenario_model.ScenarioItem(item_id=201)],  # Reward: 4 -  A New Kind of Autumn - Story 1
    482: [live_model.LiveItem(item_id=478)],  # Reward: Daisuki Dattara Daijoubu!
    483: [scenario_model.ScenarioItem(item_id=202)],  # Reward: 4 -  A New Kind of Autumn - Story 2
    485: [scenario_model.ScenarioItem(item_id=182)],  # Reward: 47 - The Miracle Nine - Story 3
    486: [live_model.LiveItem(item_id=489)],  # Reward: Future Style
    487: [scenario_model.ScenarioItem(item_id=183)],  # Reward: 47 - The Miracle Nine - Story 4
    489: [scenario_model.ScenarioItem(item_id=203)],  # Reward: 4 -  A New Kind of Autumn - Story 3
    491: [scenario_model.ScenarioItem(item_id=204)],  # Reward: 4 -  A New Kind of Autumn - Story 4
    494: [scenario_model.ScenarioItem(item_id=205)],  # Reward: 5 -  An Aqours Christmas 1 - Story 1
    495: [live_model.LiveItem(item_id=491)],  # Reward: Jingle Bells ga Tomaranai
    496: [scenario_model.ScenarioItem(item_id=206)],  # Reward: 5 -  An Aqours Christmas 1 - Story 2
    499: [scenario_model.ScenarioItem(item_id=207)],  # Reward: 5 -  An Aqours Christmas 1 - Story 3
    500: [live_model.LiveItem(item_id=493)],  # Reward: Seinaru Hino Inori
    501: [scenario_model.ScenarioItem(item_id=208)],  # Reward: 5 -  An Aqours Christmas 1 - Story 4
    504: [scenario_model.ScenarioItem(item_id=209)],  # Reward: 6 -  An Aqours Christmas 2 - Story 1
    506: [scenario_model.ScenarioItem(item_id=210)],  # Reward: 6 -  An Aqours Christmas 2 - Story 2
    509: [scenario_model.ScenarioItem(item_id=211)],  # Reward: 6 -  An Aqours Christmas 2 - Story 3
    511: [scenario_model.ScenarioItem(item_id=212)],  # Reward: 6 -  An Aqours Christmas 2 - Story 4
    514: [scenario_model.ScenarioItem(item_id=213)],  # Reward: 7 - Welcoming the New Year! - Story 1
    515: [live_model.LiveItem(item_id=481)],  # Reward: Yumede Yozorawo Terashitai
    516: [scenario_model.ScenarioItem(item_id=214)],  # Reward: 7 - Welcoming the New Year! - Story 2
    519: [scenario_model.ScenarioItem(item_id=215)],  # Reward: 7 - Welcoming the New Year! - Story 3
    521: [scenario_model.ScenarioItem(item_id=216)],  # Reward: 7 - Welcoming the New Year! - Story 4
    524: [scenario_model.ScenarioItem(item_id=217)],  # Reward: 8 - Setsubun and Valentine's - Story 1
    525: [live_model.LiveItem(item_id=483)],  # Reward: Mijuku DREAMER
    526: [scenario_model.ScenarioItem(item_id=218)],  # Reward: 8 - Setsubun and Valentine's - Story 2
    529: [scenario_model.ScenarioItem(item_id=219)],  # Reward: 8 - Setsubun and Valentine's - Story 3
    531: [scenario_model.ScenarioItem(item_id=220)],  # Reward: 8 - Setsubun and Valentine's - Story 4
    534: [scenario_model.ScenarioItem(item_id=221)],  # Reward: 9 - School Idols on Deck! - Story 1
    535: [live_model.LiveItem(item_id=486)],  # Reward: Omoiyo Hitotsuninare
    536: [scenario_model.ScenarioItem(item_id=222)],  # Reward: 9 - School Idols on Deck! - Story 2
    539: [scenario_model.ScenarioItem(item_id=223)],  # Reward: 9 - School Idols on Deck! - Story 3
    541: [scenario_model.ScenarioItem(item_id=224)],  # Reward: 9 - School Idols on Deck! - Story 4
    544: [scenario_model.ScenarioItem(item_id=225)],  # Reward: 10 - The Aqours Theater Troupe! - Story 1
    545: [live_model.LiveItem(item_id=487)],  # Reward: MIRAI TICKET
    546: [scenario_model.ScenarioItem(item_id=226)],  # Reward: 10 - The Aqours Theater Troupe! - Story 2
    549: [scenario_model.ScenarioItem(item_id=227)],  # Reward: 10 - The Aqours Theater Troupe! - Story 3
    551: [scenario_model.ScenarioItem(item_id=228)],  # Reward: 10 - The Aqours Theater Troupe! - Story 4
    554: [scenario_model.ScenarioItem(item_id=229)],  # Reward: 11 - Spring, the Sea, and Events - Story 1
    555: [live_model.LiveItem(item_id=503)],  # Reward: HAPPY PARTY TRAIN
    556: [scenario_model.ScenarioItem(item_id=230)],  # Reward: 11 - Spring, the Sea, and Events - Story 2
    559: [scenario_model.ScenarioItem(item_id=231)],  # Reward: 11 - Spring, the Sea, and Events - Story 3
    561: [scenario_model.ScenarioItem(item_id=232)],  # Reward: 11 - Spring, the Sea, and Events - Story 4
    564: [scenario_model.ScenarioItem(item_id=233)],  # Reward: 12 - Fixing Hanamaru's Weak Spot - Story 1
    565: [live_model.LiveItem(item_id=507)],  # Reward: Humming Friend
    566: [scenario_model.ScenarioItem(item_id=234)],  # Reward: 12 - Fixing Hanamaru's Weak Spot - Story 2
    569: [scenario_model.ScenarioItem(item_id=235)],  # Reward: 12 - Fixing Hanamaru's Weak Spot - Story 3
    571: [scenario_model.ScenarioItem(item_id=236)],  # Reward: 12 - Fixing Hanamaru's Weak Spot - Story 4
    574: [scenario_model.ScenarioItem(item_id=237)],  # Reward: 13 - Shiitake's Big Adventure - Story 1
    575: [live_model.LiveItem(item_id=508)],  # Reward: Sunshine Pikkapika Ondo
    576: [scenario_model.ScenarioItem(item_id=238)],  # Reward: 13 - Shiitake's Big Adventure - Story 2
    579: [scenario_model.ScenarioItem(item_id=239)],  # Reward: 13 - Shiitake's Big Adventure - Story 3
    581: [scenario_model.ScenarioItem(item_id=240)],  # Reward: 13 - Shiitake's Big Adventure - Story 4
    584: [scenario_model.ScenarioItem(item_id=241)],  # Reward: 14 - Come to Uchiura, Sea Girls! - Story 1
    585: [live_model.LiveItem(item_id=513)],  # Reward: SKY JOURNEY
    586: [scenario_model.ScenarioItem(item_id=242)],  # Reward: 14 - Come to Uchiura, Sea Girls! - Story 2
    589: [scenario_model.ScenarioItem(item_id=243)],  # Reward: 14 - Come to Uchiura, Sea Girls! - Story 3
    590: [live_model.LiveItem(item_id=514)],  # Reward: Shojo Ijo no Koi ga Shitai
    591: [scenario_model.ScenarioItem(item_id=244)],  # Reward: 14 - Come to Uchiura, Sea Girls! - Story 4
    594: [scenario_model.ScenarioItem(item_id=245)],  # Reward: 15 - Aqours Housing - Story 1
    595: [live_model.LiveItem(item_id=471)],  # Reward: Yozorawa Nandemo Shitteruno?
    596: [scenario_model.ScenarioItem(item_id=246)],  # Reward: 15 - Aqours Housing - Story 2
    599: [scenario_model.ScenarioItem(item_id=247)],  # Reward: 15 - Aqours Housing - Story 3
    600: [live_model.LiveItem(item_id=480)],  # Reward: Tokimeki Bunruigaku
    601: [scenario_model.ScenarioItem(item_id=248)],  # Reward: 15 - Aqours Housing - Story 4
    604: [scenario_model.ScenarioItem(item_id=249)],  # Reward: 16 - Fortuneteller Yohane - Story 1
    605: [live_model.LiveItem(item_id=488)],  # Reward: Guilty Night, Guilty Kiss!
    606: [scenario_model.ScenarioItem(item_id=250)],  # Reward: 16 - Fortuneteller Yohane - Story 2
    609: [scenario_model.ScenarioItem(item_id=251)],  # Reward: 16 - Fortuneteller Yohane - Story 3
    610: [live_model.LiveItem(item_id=516)],  # Reward: Mirai no Bokura wa Shitteru yo
    611: [scenario_model.ScenarioItem(item_id=252)],  # Reward: 16 - Fortuneteller Yohane - Story 4
    614: [scenario_model.ScenarioItem(item_id=253)],  # Reward: 17 - Hot Spring Holiday! - Story 1
    615: [live_model.LiveItem(item_id=517)],  # Reward: Yuki wa Doko ni? Kimi no Mune ni!
    616: [scenario_model.ScenarioItem(item_id=254)],  # Reward: 17 - Hot Spring Holiday! - Story 2
    619: [scenario_model.ScenarioItem(item_id=255)],  # Reward: 17 - Hot Spring Holiday! - Story 3
    620: [live_model.LiveItem(item_id=509)],  # Reward: Landing action Yeah!!
    621: [scenario_model.ScenarioItem(item_id=256)],  # Reward: 17 - Hot Spring Holiday! - Story 4
    624: [scenario_model.ScenarioItem(item_id=257)],  # Reward: 18 - Survive Flu Season! - Story 1
    625: [live_model.LiveItem(item_id=485)],  # Reward: Pops heart de Odorundamon!
    626: [scenario_model.ScenarioItem(item_id=258)],  # Reward: 18 - Survive Flu Season! - Story 2
    629: [scenario_model.ScenarioItem(item_id=259)],  # Reward: 18 - Survive Flu Season! - Story 3
    630: [live_model.LiveItem(item_id=490)],  # Reward: Soramo Kokoromo Harerukara
    631: [scenario_model.ScenarioItem(item_id=260)],  # Reward: 18 - Survive Flu Season! - Story 4
    634: [scenario_model.ScenarioItem(item_id=261)],  # Reward: 19 - Our Countdown Live - Story 1
    635: [live_model.LiveItem(item_id=492)],  # Reward: Waku-Waku-Week!
    636: [scenario_model.ScenarioItem(item_id=262)],  # Reward: 19 - Our Countdown Live - Story 2
    639: [scenario_model.ScenarioItem(item_id=263)],  # Reward: 19 - Our Countdown Live - Story 3
    640: [live_model.LiveItem(item_id=497)],  # Reward: Daydream Warrior
    641: [scenario_model.ScenarioItem(item_id=264)],  # Reward: 19 - Our Countdown Live - Story 4
    644: [scenario_model.ScenarioItem(item_id=265)],  # Reward: 20 - The Numazu Snow Festival! - Story 1
    645: [live_model.LiveItem(item_id=499)],  # Reward: G Senjono Cinderella
    646: [scenario_model.ScenarioItem(item_id=266)],  # Reward: 20 - The Numazu Snow Festival! - Story 2
    649: [scenario_model.ScenarioItem(item_id=267)],  # Reward: 20 - The Numazu Snow Festival! - Story 3
    650: [live_model.LiveItem(item_id=500)],  # Reward: Thrilling One-way
    651: [scenario_model.ScenarioItem(item_id=268)],  # Reward: 20 - The Numazu Snow Festival! - Story 4
    654: [scenario_model.ScenarioItem(item_id=269)],  # Reward: 21 - Aqours Shiny Live Broadcast - Story 1
    655: [live_model.LiveItem(item_id=504)],  # Reward: Taiyo o Oi kakero!
    656: [scenario_model.ScenarioItem(item_id=270)],  # Reward: 21 - Aqours Shiny Live Broadcast - Story 2
    659: [scenario_model.ScenarioItem(item_id=271)],  # Reward: 21 - Aqours Shiny Live Broadcast - Story 3
    660: [live_model.LiveItem(item_id=518)],  # Reward: MY Mai☆TONIGHT
    661: [scenario_model.ScenarioItem(item_id=272)],  # Reward: 21 - Aqours Shiny Live Broadcast - Story 4
    664: [scenario_model.ScenarioItem(item_id=273)],  # Reward: 22 - Indulging Dear Dia - Story 1
    665: [live_model.LiveItem(item_id=524)],  # Reward: MIRACLE WAVE
    666: [scenario_model.ScenarioItem(item_id=274)],  # Reward: 22 - Indulging Dear Dia - Story 2
    669: [scenario_model.ScenarioItem(item_id=275)],  # Reward: 22 - Indulging Dear Dia - Story 3
    670: [live_model.LiveItem(item_id=525)],  # Reward: Awaken the power
    671: [scenario_model.ScenarioItem(item_id=276)],  # Reward: 22 - Indulging Dear Dia - Story 4
    674: [scenario_model.ScenarioItem(item_id=277)],  # Reward: 23 - A Day Out on Golden Week - Story 1
    675: [live_model.LiveItem(item_id=527)],  # Reward: WATER BLUE NEW WORLD
    676: [scenario_model.ScenarioItem(item_id=278)],  # Reward: 23 - A Day Out on Golden Week - Story 2
    679: [scenario_model.ScenarioItem(item_id=279)],  # Reward: 23 - A Day Out on Golden Week - Story 3
    680: [live_model.LiveItem(item_id=528)],  # Reward: WONDERFUL STORIES
    681: [scenario_model.ScenarioItem(item_id=280)],  # Reward: 23 - A Day Out on Golden Week - Story 4
    684: [scenario_model.ScenarioItem(item_id=281)],  # Reward: 24 - Off to the Beach - Story 1
    685: [live_model.LiveItem(item_id=510)],  # Reward: Kinmirai Happy End
    686: [scenario_model.ScenarioItem(item_id=282)],  # Reward: 24 - Off to the Beach - Story 2
    689: [scenario_model.ScenarioItem(item_id=283)],  # Reward: 24 - Off to the Beach - Story 3
    690: [live_model.LiveItem(item_id=512)],  # Reward: KOWAREYASUKI
    691: [scenario_model.ScenarioItem(item_id=284)],  # Reward: 24 - Off to the Beach - Story 4
    694: [scenario_model.ScenarioItem(item_id=285)],  # Reward: 25 - Summer Arrives! - Story 1
    695: [live_model.LiveItem(item_id=515)],  # Reward: GALAXY HidE and SeeK
    696: [scenario_model.ScenarioItem(item_id=286)],  # Reward: 25 - Summer Arrives! - Story 2
    699: [scenario_model.ScenarioItem(item_id=287)],  # Reward: 25 - Summer Arrives! - Story 3
    700: [live_model.LiveItem(item_id=519)],  # Reward: Shadow gate to love
    701: [scenario_model.ScenarioItem(item_id=288)],  # Reward: 25 - Summer Arrives! - Story 4
    704: [scenario_model.ScenarioItem(item_id=289)],  # Reward: 26 - Welcome to Numazu & Uchiura! - Story 1
    705: [live_model.LiveItem(item_id=543)],  # Reward: SELF CONTROL!!
    706: [scenario_model.ScenarioItem(item_id=290)],  # Reward: 26 - Welcome to Numazu & Uchiura! - Story 2
    709: [scenario_model.ScenarioItem(item_id=291)],  # Reward: 26 - Welcome to Numazu & Uchiura! - Story 3
    710: [live_model.LiveItem(item_id=545)],  # Reward: CRASH MIND
    711: [scenario_model.ScenarioItem(item_id=292)],  # Reward: 26 - Welcome to Numazu & Uchiura! - Story 4
    714: [scenario_model.ScenarioItem(item_id=293)],  # Reward: 27 - Saint Snow Comes to Uchiura - Story 1
    715: [live_model.LiveItem(item_id=546)],  # Reward: DROPOUT!?
    716: [scenario_model.ScenarioItem(item_id=294)],  # Reward: 27 - Saint Snow Comes to Uchiura - Story 2
    719: [scenario_model.ScenarioItem(item_id=295)],  # Reward: 27 - Saint Snow Comes to Uchiura - Story 3
    720: [live_model.LiveItem(item_id=530)],  # Reward: Kaigandori de Matteru yo
    721: [scenario_model.ScenarioItem(item_id=296)],  # Reward: 27 - Saint Snow Comes to Uchiura - Story 4
    724: [scenario_model.ScenarioItem(item_id=297)],  # Reward: 28 - A Lunar Observation Party - Story 1
    725: [live_model.LiveItem(item_id=537)],  # Reward: INNOCENT BIRD
    726: [scenario_model.ScenarioItem(item_id=298)],  # Reward: 28 - A Lunar Observation Party - Story 2
    729: [scenario_model.ScenarioItem(item_id=299)],  # Reward: 28 - A Lunar Observation Party - Story 3
    730: [live_model.LiveItem(item_id=548)],  # Reward: "MY LIST" to you!
    731: [scenario_model.ScenarioItem(item_id=300)],  # Reward: 28 - A Lunar Observation Party - Story 4
    734: [scenario_model.ScenarioItem(item_id=301)],  # Reward: 29 - Intra-club Field Day - Story 1
    735: [live_model.LiveItem(item_id=526)],  # Reward: One More Sunshine Story
    736: [scenario_model.ScenarioItem(item_id=302)],  # Reward: 29 - Intra-club Field Day - Story 2
    739: [scenario_model.ScenarioItem(item_id=303)],  # Reward: 29 - Intra-club Field Day - Story 3
    740: [live_model.LiveItem(item_id=529)],  # Reward: Oyasuminasan!
    741: [scenario_model.ScenarioItem(item_id=304)],  # Reward: 29 - Intra-club Field Day - Story 4
    744: [scenario_model.ScenarioItem(item_id=305)],  # Reward: 30 - Our Light Show - Story 1
    745: [live_model.LiveItem(item_id=532)],  # Reward: in this unstable world
    746: [scenario_model.ScenarioItem(item_id=306)],  # Reward: 30 - Our Light Show - Story 2
    749: [scenario_model.ScenarioItem(item_id=307)],  # Reward: 30 - Our Light Show - Story 3
    750: [live_model.LiveItem(item_id=531)],  # Reward: Pianoforte Monologue
    751: [scenario_model.ScenarioItem(item_id=308)],  # Reward: 30 - Our Light Show - Story 4
    754: [scenario_model.ScenarioItem(item_id=309)],  # Reward: 31 - An Aqours New Year - Story 1
    755: [live_model.LiveItem(item_id=534)],  # Reward: Beginner's Sailing
    756: [scenario_model.ScenarioItem(item_id=310)],  # Reward: 31 - An Aqours New Year - Story 2
    759: [scenario_model.ScenarioItem(item_id=311)],  # Reward: 31 - An Aqours New Year - Story 3
    760: [live_model.LiveItem(item_id=536)],  # Reward: RED GEM WINK
    761: [scenario_model.ScenarioItem(item_id=312)],  # Reward: 31 - An Aqours New Year - Story 4
    764: [scenario_model.ScenarioItem(item_id=313)],  # Reward: 32 - An Aqours Setsubun! - Story 1
    765: [live_model.LiveItem(item_id=535)],  # Reward: WHITE FIRST LOVE
    766: [scenario_model.ScenarioItem(item_id=314)],  # Reward: 32 - An Aqours Setsubun! - Story 2
    769: [scenario_model.ScenarioItem(item_id=315)],  # Reward: 32 - An Aqours Setsubun! - Story 3
    770: [live_model.LiveItem(item_id=539)],  # Reward: New winding road
    771: [scenario_model.ScenarioItem(item_id=316)],  # Reward: 32 - An Aqours Setsubun! - Story 4
    774: [scenario_model.ScenarioItem(item_id=317)],  # Reward: 33 - White Day Secret - Story 1
    775: [live_model.LiveItem(item_id=538)],  # Reward: SAKANAKANANDAKA?
    776: [scenario_model.ScenarioItem(item_id=318)],  # Reward: 33 - White Day Secret - Story 2
    779: [scenario_model.ScenarioItem(item_id=319)],  # Reward: 33 - White Day Secret - Story 3
    780: [live_model.LiveItem(item_id=540)],  # Reward: KISEKIHIKARU
    781: [scenario_model.ScenarioItem(item_id=320)],  # Reward: 33 - White Day Secret - Story 4
    784: [scenario_model.ScenarioItem(item_id=321)],  # Reward: 34 - Spring Has Sprung! - Story 1
    785: [live_model.LiveItem(item_id=542)],  # Reward: Guilty Eyes Fever
    786: [scenario_model.ScenarioItem(item_id=322)],  # Reward: 34 - Spring Has Sprung! - Story 2
    789: [scenario_model.ScenarioItem(item_id=323)],  # Reward: 34 - Spring Has Sprung! - Story 3
    790: [live_model.LiveItem(item_id=547)],  # Reward: P.S. no Mukougawa
    791: [scenario_model.ScenarioItem(item_id=324)],  # Reward: 34 - Spring Has Sprung! - Story 4
    794: [scenario_model.ScenarioItem(item_id=325)],  # Reward: 35 - Time for Aqours to Advertise - Story 1
    795: [live_model.LiveItem(item_id=558)],  # Reward: LONELY TUNING
    796: [scenario_model.ScenarioItem(item_id=326)],  # Reward: 35 - Time for Aqours to Advertise - Story 2
    799: [scenario_model.ScenarioItem(item_id=327)],  # Reward: 35 - Time for Aqours to Advertise - Story 3
    800: [live_model.LiveItem(item_id=541)],  # Reward: Hop Step Yippee!
    801: [scenario_model.ScenarioItem(item_id=328)],  # Reward: 35 - Time for Aqours to Advertise - Story 4
    804: [scenario_model.ScenarioItem(item_id=329)],  # Reward: 36 - School Idol Festival - Story 1
    805: [live_model.LiveItem(item_id=570)],  # Reward: No.10
    806: [scenario_model.ScenarioItem(item_id=330)],  # Reward: 36 - School Idol Festival - Story 2
    810: [live_model.LiveItem(item_id=544)],  # Reward: Thank you, FRIENDS!!
    811: [scenario_model.ScenarioItem(item_id=332)],  # Reward: 36 - School Idol Festival - Story 4
    814: [live_model.LiveItem(item_id=555)],  # Reward: Hajimari Road
    817: [live_model.LiveItem(item_id=556)],  # Reward: Marine Border Parasol
    820: [live_model.LiveItem(item_id=557)],  # Reward: Yosoku Fukano Driving!
    823: [live_model.LiveItem(item_id=564)],  # Reward: Bokura no Hashittekita Michi wa...
    826: [live_model.LiveItem(item_id=565)],  # Reward: Next SPARKLING!!
    829: [live_model.LiveItem(item_id=563)],  # Reward: Toso Meiso Mobius Loop
    832: [live_model.LiveItem(item_id=562)],  # Reward: Hop? Stop? Nonstop!
    835: [live_model.LiveItem(item_id=567)],  # Reward: Believe again
    838: [live_model.LiveItem(item_id=566)],  # Reward: Brightest Melody
    841: [live_model.LiveItem(item_id=568)],  # Reward: Over The Next Rainbow
    844: [live_model.LiveItem(item_id=569)],  # Reward: Sakura Bye Bye
    847: [live_model.LiveItem(item_id=574)],  # Reward: Sotsugyo desu ne
    850: [live_model.LiveItem(item_id=577)],  # Reward: Guilty!? Farewell party
    853: [live_model.LiveItem(item_id=571)],  # Reward: Jump up HIGH!!
    856: [live_model.LiveItem(item_id=572)],  # Reward: Bouken Type A, B, C!!
    859: [live_model.LiveItem(item_id=573)],  # Reward: Deep Resonance
    862: [live_model.LiveItem(item_id=575)],  # Reward: MITAIKEN HORIZON
    865: [live_model.LiveItem(item_id=581)],  # Reward: New Romantic Sailors
    868: [live_model.LiveItem(item_id=582)],  # Reward: Braveheart Coaster
    871: [live_model.LiveItem(item_id=586)],  # Reward: Amazing Travel DNA
    874: [live_model.LiveItem(item_id=610)],  # Reward: i-n-g, I TRY!!
    877: [live_model.LiveItem(item_id=611)],  # Reward: Love Pulsar
    880: [live_model.LiveItem(item_id=612)],  # Reward: CHANGELESS
    883: [live_model.LiveItem(item_id=613)],  # Reward: Kuchu Renairon
    886: [live_model.LiveItem(item_id=615)],  # Reward: Phantom Rocket Adventure
    889: [live_model.LiveItem(item_id=616)],  # Reward: Kodoku Teleport
    892: [live_model.LiveItem(item_id=618)],  # Reward: Maze Sekai
    895: [live_model.LiveItem(item_id=533)],  # Reward: Kimi no Hitomi o Meguru Boken
    898: [live_model.LiveItem(item_id=609)],  # Reward: Dance with Minotaurus
    900: [live_model.LiveItem(item_id=608)],  # Reward: A song for You! You? You!!
    904: [live_model.LiveItem(item_id=620)],  # Reward: Natte shimatta!
    908: [live_model.LiveItem(item_id=622)],  # Reward: Bokura wa Ima no Naka de (LittleMore-Rock Mix)
    912: [live_model.LiveItem(item_id=623)],  # Reward: No brand girls (GRP-Explosion Mix)
    916: [live_model.LiveItem(item_id=624)],  # Reward: START:DASH!!（Bitter-Sweet Mix）
    920: [live_model.LiveItem(item_id=625)],  # Reward: Wonderful Rush（Heavy-Rush Mix）
    924: [live_model.LiveItem(item_id=626)],  # Reward: Music S.T.A.R.T!!（SKA-Feel Mix）
    928: [live_model.LiveItem(item_id=627)],  # Reward: Pure girls project（Super-Mondo Mix）
    932: [live_model.LiveItem(item_id=628)],  # Reward: Cutie Panther (Metal-Panther Mix)
    936: [live_model.LiveItem(item_id=629)],  # Reward: Binetsu kara Mystery (TeKe-TeKe ELEKI Mix)
    940: [live_model.LiveItem(item_id=617)],  # Reward: Fantastic Departure!
    944: [live_model.LiveItem(item_id=619)],  # Reward: Dazzling White Town
    948: [item_model.Item(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=3, amount=10)],
    949: [item_model.Item(add_type=const.ADD_TYPE.EXCHANGE_POINT, item_id=2, amount=20)],
    950: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=23, amount=9)],
    951: [item_model.Item(add_type=const.ADD_TYPE.EXCHANGE_POINT, item_id=3, amount=10)],
    952: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=5, amount=25)],
    953: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=24, amount=9)],
    954: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=14101)],
    955: [item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=2227)],
    956: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=93, amount=9)],
    957: [item.loveca(50)],
    10010009: [item.loveca(1)],
    10040008: [item.loveca(1)],
    10090002: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=6)],
    10090003: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=7)],
    10090004: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=8)],
    10090005: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=9)],
    10090006: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=10)],
    10090007: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=11)],
    10090009: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=13)],
    10090011: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=15)],
    10090022: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=30)],
    10090023: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=31)],
    10090024: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=32)],
    10090025: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=33)],
    10090026: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=34)],
    10090027: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=35)],
    10090028: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=36)],
    10090029: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=37)],
    10090030: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=38)],
    10090031: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=39)],
    10090032: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=40)],
    10090033: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=41)],
    10090041: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=1)],
    10090162: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=269)],
    10093826: [item_model.Item(add_type=const.ADD_TYPE.BACKGROUND, item_id=227)],
    10093843: [item.loveca(3)],
    10093844: [item.loveca(2)],
    10093850: [item_model.Item(add_type=const.ADD_TYPE.BACKGROUND, item_id=228)],
    10100010: [item.game_coin(40000)],
    10180011: [item.loveca(1)],
    10190014: [item.loveca(1)],
    10200007: [item.loveca(1)],
    10260004: [item.social_point(4000)],
    10290001: [item_model.Item(add_type=const.ADD_TYPE.AWARD, item_id=2)],
    10290004: [
        item_model.Item(add_type=const.ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=2),
        item_model.Item(add_type=const.ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=1),
        item_model.Item(add_type=const.ADD_TYPE.SCHOOL_IDOL_SKILL, item_id=3),
    ],
    10290006: [live_model.LiveItem(item_id=533)],
    10290009: [scenario_model.ScenarioItem(item_id=3006)],
    10290011: [scenario_model.ScenarioItem(item_id=3016)],  # Reward: [Story] - Story 2
    10290012: [scenario_model.ScenarioItem(item_id=3017)],  # Reward: [Story] - Story 3
    10290014: [scenario_model.ScenarioItem(item_id=3007)],
    10290016: [scenario_model.ScenarioItem(item_id=3020)],  # Reward: [Story] - Story 2
    10290017: [scenario_model.ScenarioItem(item_id=3021)],  # Reward: [Story] - Story 3
    10290019: [scenario_model.ScenarioItem(item_id=3008)],
    10290021: [scenario_model.ScenarioItem(item_id=3024)],  # Reward: [Story] - Story 2
    10290022: [scenario_model.ScenarioItem(item_id=3025)],  # Reward: [Story] - Story 3
    10290024: [scenario_model.ScenarioItem(item_id=3009)],
    10290025: [scenario_model.ScenarioItem(item_id=3010)],
    10290026: [scenario_model.ScenarioItem(item_id=3011)],
    10290027: [scenario_model.ScenarioItem(item_id=3012)],
    10290028: [scenario_model.ScenarioItem(item_id=3013)],
    10290029: [scenario_model.ScenarioItem(item_id=3014)],
    10290030: [scenario_model.ScenarioItem(item_id=3029)],
    10290031: [scenario_model.ScenarioItem(item_id=3030)],
    10290032: [scenario_model.ScenarioItem(item_id=3031)],
    10290035: [scenario_model.ScenarioItem(item_id=3034)],
    10290036: [item_model.Item(add_type=const.ADD_TYPE.UNIT_MAX, item_id=0, amount=100)],
    10290037: [scenario_model.ScenarioItem(item_id=3015)],  # Reward: [Story] - Story 1
    10290038: [scenario_model.ScenarioItem(item_id=3019)],  # Reward: [Story] - Story 1
    10290039: [scenario_model.ScenarioItem(item_id=3023)],  # Reward: [Story] - Story 1
    10290040: [
        scenario_model.ScenarioItem(item_id=3001)
    ],  # Reward: Real-Life Escape Game - Prologue - Case of the Missing Trunk
    10290050: [scenario_model.ScenarioItem(item_id=3037)],  # Reward: Enchanting Everyone - Enchanting Everyone
    10290050: [scenario_model.ScenarioItem(item_id=3040)],  # Reward: Fantastic Stage - Fantastic Stage
    10290050: [
        scenario_model.ScenarioItem(item_id=3043)
    ],  # Reward: Nijigasaki★Magical★Story - Nijigasaki★Magical★Story
    10290051: [scenario_model.ScenarioItem(item_id=3038)],  # Reward: Enchanting Everyone - Story 2
    10290053: [scenario_model.ScenarioItem(item_id=3041)],  # Reward: Fantastic Stage - Story 2
    10290055: [scenario_model.ScenarioItem(item_id=3044)],  # Reward: Nijigasaki★Magical★Story - Story 2
    10290058: [scenario_model.ScenarioItem(item_id=3052)],
    10290059: [scenario_model.ScenarioItem(item_id=3051)],
    10290061: [scenario_model.ScenarioItem(item_id=3048)],
    10290062: [scenario_model.ScenarioItem(item_id=3057)],
    10290063: [scenario_model.ScenarioItem(item_id=3055)],
    10290064: [scenario_model.ScenarioItem(item_id=3053)],
    10290065: [scenario_model.ScenarioItem(item_id=3058)],
    10290066: [scenario_model.ScenarioItem(item_id=3054)],
    10290067: [scenario_model.ScenarioItem(item_id=3056)],
    10290068: [scenario_model.ScenarioItem(item_id=3050)],
    10290069: [scenario_model.ScenarioItem(item_id=3047)],
    10290074: [scenario_model.ScenarioItem(item_id=3061)],
    10290076: [scenario_model.ScenarioItem(item_id=3059)],
    10290078: [scenario_model.ScenarioItem(item_id=3060)],
    10290080: [item_model.Item(add_type=const.ADD_TYPE.UNIT_MAX, item_id=0, amount=100)],
    10290081: [scenario_model.ScenarioItem(item_id=3063)],  # Reward: [Story] - μ's Have Come to Town!
    10290082: [scenario_model.ScenarioItem(item_id=3064)],  # Reward: [Story] - Aqours Have Come to Town!
    10290088: [scenario_model.ScenarioItem(item_id=3062)],
    10290095: [
        scenario_model.ScenarioItem(item_id=3043),
        scenario_model.ScenarioItem(item_id=3044),
        scenario_model.ScenarioItem(item_id=3045),
    ],
    10290096: [live_model.LiveItem(item_id=621)],
    10290097: [live_model.LiveItem(item_id=632)],
    10290098: [scenario_model.ScenarioItem(item_id=3070)],  # Reward: [Story] - μ'sの天カス学園体験記 1話
    10290099: [scenario_model.ScenarioItem(item_id=3071)],  # Reward: [Story] - μ'sの天カス学園体験記 2話
    10290100: [scenario_model.ScenarioItem(item_id=3072)],  # Reward: [Story] - μ'sの天カス学園体験記 3話
    10290102: [scenario_model.ScenarioItem(item_id=3074)],  # Reward: [Story] - Aqoursの天カス学園体験記 1話
    10290103: [scenario_model.ScenarioItem(item_id=3075)],  # Reward: [Story] - Aqoursの天カス学園体験記 2話
    10290104: [scenario_model.ScenarioItem(item_id=3076)],  # Reward: [Story] - Aqoursの天カス学園体験記 3話
    10290106: [live_model.LiveItem(item_id=637)],
    10290107: [scenario_model.ScenarioItem(item_id=3078)],
    10290108: [scenario_model.ScenarioItem(item_id=3079)],
    10290109: [scenario_model.ScenarioItem(item_id=3080)],
    10290110: [scenario_model.ScenarioItem(item_id=3081)],
    10290111: [scenario_model.ScenarioItem(item_id=3082)],
    10290112: [scenario_model.ScenarioItem(item_id=3083)],
    10290113: [scenario_model.ScenarioItem(item_id=3084)],
    10290114: [scenario_model.ScenarioItem(item_id=3085)],
    10290115: [live_model.LiveItem(item_id=641)],
    10290116: [live_model.LiveItem(item_id=645)],
    10290117: [live_model.LiveItem(item_id=649)],
    10290118: [live_model.LiveItem(item_id=653)],
    10290119: [live_model.LiveItem(item_id=659)],
    10290120: [live_model.LiveItem(item_id=664)],
    10290121: [live_model.LiveItem(item_id=672)],
    10290122: [live_model.LiveItem(item_id=688)],
    10290123: [live_model.LiveItem(item_id=698)],
    10290124: [live_model.LiveItem(item_id=700)],
    10290127: [
        scenario_model.ScenarioItem(item_id=3088)
    ],  # Reward: After School with Liella! - After School with Liella! 1
    10290128: [
        scenario_model.ScenarioItem(item_id=3089)
    ],  # Reward: After School with Liella! - After School with Liella! 2
    10290129: [
        scenario_model.ScenarioItem(item_id=3090)
    ],  # Reward: After School with Liella! - After School with Liella! 3
    10290132: [
        scenario_model.ScenarioItem(item_id=3092)
    ],  # Reward: Liella!'s Hot-Pot Party - Liella!'s Hot-Pot Party 1
    10290133: [
        scenario_model.ScenarioItem(item_id=3093)
    ],  # Reward: Liella!'s Hot-Pot Party - Liella!'s Hot-Pot Party 2
    10290134: [
        scenario_model.ScenarioItem(item_id=3094)
    ],  # Reward: Liella!'s Hot-Pot Party - Liella!'s Hot-Pot Party 3
    10290136: [
        live_model.LiveItem(item_id=631),
        live_model.LiveItem(item_id=636),
        live_model.LiveItem(item_id=640),
    ],
    10290137: [
        live_model.LiveItem(item_id=650),
        live_model.LiveItem(item_id=651),
        live_model.LiveItem(item_id=652),
    ],
    10290138: [
        live_model.LiveItem(item_id=658),
        live_model.LiveItem(item_id=661),
        live_model.LiveItem(item_id=656),
    ],
    10290139: [
        live_model.LiveItem(item_id=663),
        live_model.LiveItem(item_id=687),
    ],
    10290142: [live_model.LiveItem(item_id=696)],
    10290143: [scenario_model.ScenarioItem(item_id=3098)],  # Reward: Retro Pop Liella! - Retro Pop Liella! 1
    10290144: [scenario_model.ScenarioItem(item_id=3099)],  # Reward: Retro Pop Liella! - Retro Pop Liella! 2
    10290145: [scenario_model.ScenarioItem(item_id=3100)],  # Reward: Retro Pop Liella! - Retro Pop Liella! 3
    10290147: [live_model.LiveItem(item_id=691)],
    10290148: [live_model.LiveItem(item_id=726)],
    10290149: [live_model.LiveItem(item_id=728)],
    10290150: [live_model.LiveItem(item_id=733)],
    10290151: [live_model.LiveItem(item_id=739)],
    10290152: [live_model.LiveItem(item_id=745)],
    10290153: [live_model.LiveItem(item_id=750)],
    10290154: [live_model.LiveItem(item_id=757)],
    10290165: [scenario_model.ScenarioItem(item_id=3102)],  # Reward: Tail the 2nd Years! - Tail the 2nd Years! 1
    10290166: [scenario_model.ScenarioItem(item_id=3103)],  # Reward: Tail the 2nd Years! - Tail the 2nd Years! 2
    10290167: [scenario_model.ScenarioItem(item_id=3104)],  # Reward: Tail the 2nd Years! - Tail the 2nd Years! 3
    10370001: [live_model.LiveItem(item_id=13)],  # Reward: Bokura wa Ima no Naka de
    10370002: [live_model.LiveItem(item_id=20)],  # Reward: Kitto Seishun ga Kikoeru
    10370003: [live_model.LiveItem(item_id=214)],  # Reward: It's our miraculous time
    10370004: [live_model.LiveItem(item_id=230)],  # Reward: Donna Tokimo Zutto
    10370005: [live_model.LiveItem(item_id=419)],  # Reward: Angelic Angel
    10370006: [live_model.LiveItem(item_id=442)],  # Reward: SUNNY DAY SONG
    10370007: [live_model.LiveItem(item_id=444)],  # Reward: Bokutachi wa Hitotsu no Hikari
    10370008: [live_model.LiveItem(item_id=447)],  # Reward: HEART to HEART!
    10370009: [live_model.LiveItem(item_id=448)],  # Reward: Arashi no Naka no Koi dakara
    10370010: [live_model.LiveItem(item_id=141)],  # Reward: Takaramonos
    10370011: [live_model.LiveItem(item_id=146)],  # Reward: Paradise Live
    10370012: [live_model.LiveItem(item_id=460)],  # Reward: MOMENT RING
    20010007: [
        item.loveca(1),
        item.game_coin(10000),
        item.social_point(200),
    ],
    20010015: [
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=89),
        item_model.Item(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010016: [
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=1024),
        item_model.Item(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010017: [
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=382),
        item_model.Item(add_type=const.ADD_TYPE.RECOVER_LP_ITEM, item_id=1),
    ],
    20010018: [
        item.loveca(1),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=632),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=1142),
    ],
    20010019: [
        item.loveca(1),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=385),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=1354),
    ],
    20010020: [
        item.loveca(1),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=384),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=1355),
    ],
    20010021: [
        item.loveca(1),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=383),
        item_model.Item(add_type=const.ADD_TYPE.UNIT, item_id=1356),
    ],
    50000001: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1597)],
    50000006: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1601)],
    50010001: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1)],
    50010002: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=2)],
    50010003: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=3)],
    50010004: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=4)],
    50010005: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=5)],
    50010006: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=6)],
    50010007: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=7)],
    50010008: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=8)],
    50010009: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=9)],
    50010190: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=190)],
    50020001: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=300)],
    50020002: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=301)],
    50020003: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=302)],
    50020004: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=303)],
    50020005: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=304)],
    50020006: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=305)],
    50020007: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=306)],
    50020008: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=307)],
    50020009: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=308)],
    50020010: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=309)],
    50020011: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=310)],
    50020012: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=311)],
    50020013: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=312)],
    50020014: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=313)],
    50020015: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=314)],
    50020016: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=315)],
    50020017: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=316)],
    50020018: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=317)],
    50020019: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=318)],
    50020020: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=319)],
    50020021: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=320)],
    50020022: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=321)],
    50020023: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=322)],
    50020024: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=323)],
    50020025: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=324)],
    50020026: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=325)],
    50020027: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=326)],
    50020028: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=327)],
    50020029: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=328)],
    50020030: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=329)],
    50020031: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=330)],
    50020032: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=331)],
    50020033: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=332)],
    50020034: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=333)],
    50020035: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=334)],
    50020036: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=335)],
    50020037: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=336)],
    50020038: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=337)],
    50020039: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=338)],
    50020040: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=339)],
    50020041: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=340)],
    50020042: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=341)],
    50020043: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=342)],
    50020044: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=343)],
    50020045: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=344)],
    50020046: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=345)],
    50020047: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=346)],
    50020048: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=347)],
    50020049: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=348)],
    50020050: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=349)],
    50020051: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=350)],
    50020052: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=351)],
    50030001: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=500)],
    50040037: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=636)],
    50040055: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=654)],
    50050001: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1857)],
    50050002: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1858)],
    50050003: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1859)],
    50050004: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1860)],
    50050007: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1863)],
    50050008: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1864)],
    50050009: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1865)],
    50050010: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1866)],
    50050011: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1867)],
    50050012: [item_model.Item(add_type=const.ADD_TYPE.MUSEUM, item_id=1868)],
    100000001: [item.game_coin(10000)],
    100000002: [item.social_point(1000)],
    100000027: [item_model.Item(add_type=const.ADD_TYPE.ITEM, item_id=5, amount=3)],
    200000001: [item.loveca(1)],
}


def get(achievement_id: int) -> list[common.AnyItem]:
    reward = ACHIEVEMENT_REWARDS.get(achievement_id)
    if reward is None:
        reward = [ACHIEVEMENT_REWARD_DEFAULT]
    return reward
