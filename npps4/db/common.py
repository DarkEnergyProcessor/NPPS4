import re

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


class PrettyPrinter:
    def __repr__(self):
        t = type(self)
        kvresult: list[str] = []

        for var in t.__annotations__.keys():
            if hasattr(self, var):
                kvresult.append(f"{var}={getattr(self, var)!r}")

        return f"{t.__name__}({', '.join(kvresult)})"


class GameDBBase(sqlalchemy.orm.DeclarativeBase, PrettyPrinter):
    type_annotation_map = type_map_override


SNAKECASE_RE1 = re.compile("(.)([A-Z][a-z]+)")
SNAKECASE_RE2 = re.compile("__([A-Z])")
SNAKECASE_RE3 = re.compile("([a-z0-9])([A-Z])")


class Base(sqlalchemy.orm.DeclarativeBase, PrettyPrinter):
    type_annotation_map = type_map_override

    @sqlalchemy.orm.declared_attr.directive
    def __tablename__(cls):
        name = cls.__name__
        name = re.sub(SNAKECASE_RE1, r"\1_\2", name)
        name = re.sub(SNAKECASE_RE2, r"_\1", name)
        name = re.sub(SNAKECASE_RE3, r"\1_\2", name)
        return name.lower()


class MaybeEncrypted:
    release_tag: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column()
    _encryption_release_id: sqlalchemy.orm.Mapped[int | None] = sqlalchemy.orm.mapped_column()
