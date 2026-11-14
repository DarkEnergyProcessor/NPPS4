from .secretbox import bt_aqua
from .secretbox import bt_aqua_10x
from .secretbox import bt_myus
from .secretbox import bt_myus_10x
from .secretbox import honor_aqua
from .secretbox import honor_lila
from .secretbox import honor_myus
from .secretbox import honor_niji
from .secretbox import regular_aqua
from .secretbox import regular_myus
from .. import schema

secretbox_data: list[schema.SecretboxData] = [
    regular_myus.data,
    honor_myus.data,
    bt_myus_10x.data,
    bt_myus.data,
    regular_aqua.data,
    honor_aqua.data,
    bt_aqua.data,
    bt_aqua_10x.data,
    honor_niji.data,
    honor_lila.data,
]
