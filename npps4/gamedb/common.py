import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.dialects.sqlite

String = sqlalchemy.String(1024)
Float = sqlalchemy.Float(15)


class MaybeEncrypted:
    release_tag: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(String, nullable=True)
    _encryption_release_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column(nullable=True)
