import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.dialects.postgresql
import sqlalchemy.dialects.mysql
import sqlalchemy.dialects.oracle
import sqlalchemy.dialects.sqlite


IDInteger = sqlalchemy.BigInteger().with_variant(sqlalchemy.dialects.sqlite.INTEGER(), "sqlite")


type_map_override = {
    str: sqlalchemy.Text(),
    float: sqlalchemy.Float(16)
    .with_variant(sqlalchemy.dialects.sqlite.REAL(), "sqlite")
    .with_variant(sqlalchemy.dialects.oracle.BINARY_DOUBLE(), "oracle")
    .with_variant(sqlalchemy.dialects.mysql.DOUBLE(), "mysql", "mariadb")
    .with_variant(sqlalchemy.dialects.postgresql.DOUBLE_PRECISION(), "postgresql"),
}


class MaybeEncrypted:
    release_tag: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    _encryption_release_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
