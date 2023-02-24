import sqlalchemy
import sqlalchemy.dialects.sqlite

from typing import cast, Union

String = sqlalchemy.String(1024)
Float = sqlalchemy.Float(15)


class MaybeEncrypted:
    release_tag = cast(Union[str, None], sqlalchemy.Column(String, nullable=True))
    _encryption_release_id = cast(Union[int, None], sqlalchemy.Column(sqlalchemy.Integer, nullable=True))
